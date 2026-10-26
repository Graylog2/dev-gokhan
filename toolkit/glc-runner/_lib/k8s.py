# -*- coding: utf-8 -*-

import re

from _lib.cmd import Cmd
from _lib.converter import JsonConverter
from _lib.converter import Base64Converter


class Debuggy:

    def __init__(self, namespace):
        self.__cmd = Cmd()
        self.__json = JsonConverter()
        self.__ns = namespace
        self.__name = None

    def __set_name(self):
        cmd_str = [
            "kubectl",
            "get",
            "pods",
            "-n",
            f"{self.__ns}",
            "-l" "app=debuggy",
            "-o",
            "json",
        ]
        output = self.__cmd.run(cmd_str)
        if output["status"] == "success":
            pod_obj = self.__json.decode(output["stdout"])
            self.__name = pod_obj["items"][0]["metadata"]["name"]
            return True
        return False

    def get_name(self):
        return self.__name

    def deploy(self):
        with open("_manifests/debuggy.yaml", "r") as fp:
            debuggy_tpl = fp.read()
            debuggy_manifest = debuggy_tpl.replace("{NAMESPACE}", self.__ns)
            cmd_str = ["kubectl", "apply", "-f", "-"]
            self.__cmd.run(cmd_str, input=debuggy_manifest.encode("UTF-8"))
            self.__set_name()
            cmd_str = [
                "kubectl",
                "wait",
                "--for=condition=Available",
                "--timeout=300s",
                "-n",
                f"{self.__ns}",
                "deployment/debuggy",
            ]
            self.__cmd.run(cmd_str)

            return True

    def destroy(self):
        with open("_manifests/debuggy.yaml", "r") as fp:
            debuggy_tpl = fp.read()
            debuggy_manifest = debuggy_tpl.replace("{NAMESPACE}", self.__ns)
            cmd_str = ["kubectl", "delete", "-f", "-"]
            self.__cmd.run(cmd_str, input=debuggy_manifest.encode("UTF-8"))


class K8S:

    def __init__(self):
        self.__cmd = Cmd()
        self.__json = JsonConverter()
        self.__base64 = Base64Converter()

    def get_namespaces(self, filter=None):
        cmd_str = ["kubectl", "get", "ns", "-o", "json"]
        response = self.__cmd.run(cmd_str)
        namespace_list = []
        if response["status"] == "success":
            raw_namespaces = response["stdout"]
            if namespaces_json := self.__json.decode(raw_namespaces):
                for item in namespaces_json["items"]:
                    if filter is None:
                        namespace_list.append(item["metadata"]["name"])
                        continue
                    if re.search(f"{filter}", item["metadata"]["name"]):
                        namespace_list.append(item["metadata"]["name"])
        return namespace_list

    def get_secret(self, namespace, secret_name, key_name):
        cmd_str = [
            "kubectl",
            "get",
            "secret",
            "-o",
            "json",
            "-n",
            namespace,
            secret_name,
        ]
        response = self.__cmd.run(cmd_str)
        if response["status"] == "success":
            try:
                raw_json = response["stdout"]
                secret_object = self.__json.decode(raw_json)
                secret_str = self.__base64.decode(secret_object["data"][key_name])
                return secret_str
            except:
                return None

        return None


class Pod:

    def __init__(self, namespace, pod):
        self.__cmd = Cmd()
        self.__ns = namespace
        self.__pod = pod

    def get_env(self, variable_name):
        cmd_str = [
            "kubectl",
            "exec",
            "--tty",
            "--stdin",
            "-n",
            f"{self.__ns}",
            f"{self.__pod}",
            "--",
            "env",
        ]
        output = self.__cmd.run(cmd_str)
        if output["status"] == "success":
            env_list = output["stdout"].split("\n")
            for env in env_list:
                if env.startswith(f"{variable_name}="):
                    return env.replace(f"{variable_name}=", "")
        return False

    def exec(self, cmd):
        response = {}
        cmd_prefix = [
            "kubectl",
            "exec",
            "--tty",
            "--stdin",
            "-n",
            f"{self.__ns}",
            f"{self.__pod}",
            "--",
        ]
        cmd_str = cmd_prefix + cmd
        try:
            output = self.__cmd.run(cmd_str)
            if output["status"] == "success":
                response["status"] = "success"
                response["output"] = output["stdout"]
                return response
            response["status"] = "failed"
            response["output"] = output["stderr"]
        except:
            pass
        return response
