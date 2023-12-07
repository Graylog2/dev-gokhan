# -*- coding: utf-8 -*-
import subprocess

class Cmd:

    def __init__(self) -> None:
        self.__response = {}

    def run(self, command, input=None, shell=False):
        try:
            p = subprocess.Popen(
                command,
                universal_newlines=False,
                shell=shell,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if input is not None:
                out, err = p.communicate(input=input, timeout=1200)
                p.wait()
            else:
                out, err = p.communicate(timeout=1200)
                p.wait()

            self.__response = {
                "stdout": out.decode('UTF-8').rstrip(),
                "stderr": err.decode('UTF-8').rstrip(),
                "status": None
            }

            if p.returncode > 0:
                self.__response['status'] = "failed"
            else:
                self.__response['status'] = "success"
            return self.__response
        except Exception as e:
            self.__response = {
                "stdout": f"Command execution failure ({e})",
                "stderr": f"Command execution failure ({e})",
                "status": "failed"
            }
            return self.__response
