#!/usr/bin/env python

from struct import pack
import exploits
from utils import (
    print_success,
    print_status,
    print_info,
    print_error,
    random_text
)

ARCH_ELF_HEADERS = {
    "armle": ("\x7f\x45\x4c\x46\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
              "\x02\x00\x28\x00\x01\x00\x00\x00\x54\x80\x00\x00\x34\x00\x00\x00"
              "\x00\x00\x00\x00\x00\x00\x00\x00\x34\x00\x20\x00\x01\x00\x00\x00"
              "\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00"
              "\x00\x80\x00\x00\xef\xbe\xad\xde\xef\xbe\xad\xde\x07\x00\x00\x00"
              "\x00\x10\x00\x00"),
    "mipsbe": ("\x7f\x45\x4c\x46\x01\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
               "\x00\x02\x00\x08\x00\x00\x00\x01\x00\x40\x00\x54\x00\x00\x00\x34"
               "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x34\x00\x20\x00\x01\x00\x00"
               "\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x40\x00\x00"
               "\x00\x40\x00\x00\xde\xad\xbe\xef\xde\xad\xbe\xef\x00\x00\x00\x07"
               "\x00\x00\x10\x00"),
    "mipsle": ("\x7f\x45\x4c\x46\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
               "\x02\x00\x08\x00\x01\x00\x00\x00\x54\x00\x40\x00\x34\x00\x00\x00"
               "\x00\x00\x00\x00\x00\x00\x00\x00\x34\x00\x20\x00\x01\x00\x00\x00"
               "\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00"
               "\x00\x00\x40\x00\xef\xbe\xad\xde\xef\xbe\xad\xde\x07\x00\x00\x00"
               "\x00\x10\x00\x00")
}


class Payload(exploits.Exploit):
    output = exploits.Option('python', 'Output type: elf/python')
    filepath = exploits.Option("/tmp/{}".format(random_text(8)), 'Output file to write')

    def __init__(self):
        if self.architecture == "armle":
            self.bigendian = False
            self.header = ARCH_ELF_HEADERS['armle']
        elif self.architecture == "mipsbe":
            self.bigendian = True
            self.header = ARCH_ELF_HEADERS['mipsbe']
        elif self.architecture == "mipsle":
            self.bigendian = False
            self.header = ARCH_ELF_HEADERS['mipsle']
        else:
            print_error("Define architecture. Supported architectures: armle, mipsbe, mipsle")
            return None

    def run(self):
        print_status("Generating payload")
        self.generate()

        if self.output == "elf":
            with open(self.filepath, 'w+') as f:
                print_status("Building ELF payload")
                content = self.generate_elf()

                print_success("Saving file {}".format(self.filepath))
                f.write(content)

        elif self.output == "python":
            print_success("Building payload for python")
            content = self.generate_python()
            print_info(content)

    def convert_ip(self, addr):
        res = ""
        for i in addr.split("."):
            res += chr(int(i))
        return res

    def convert_port(self, p):
        res = "%.4x" % int(p)
        return res.decode('hex')

    def generate_elf(self):
        elf = self.header + self.payload

        if self.bigendian:
            p_filesz = pack(">L", len(elf))
            p_memsz = pack(">L", len(elf) + len(self.payload))
        else:
            p_filesz = pack("<L", len(elf))
            p_memsz = pack("<L", len(elf) + len(self.payload))

        content = elf[:0x44] + p_filesz + p_memsz + elf[0x4c:]
        return content

    def generate_python(self):
        res = "payload = (\n    \""
        for idx, x in enumerate(self.payload):
            if idx % 15 == 0 and idx != 0:
                res += "\"\n    \""

            res += "\\x%02x" % ord(x)
        res += "\"\n)"
        return res
