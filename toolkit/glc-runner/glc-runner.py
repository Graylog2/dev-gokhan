#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from _lib.k8s import K8S
from _lib.k8s import Pod
from _lib.k8s import Debuggy
from _lib.converter import JsonConverter


k8s = K8S()
json = JsonConverter()

tenant_ns_list = k8s.get_namespaces(filter="^tenant-.*")

for namespace in tenant_ns_list:
    graylog_pod = Pod(namespace, "graylog-application-0")
    if (os_conn_str := graylog_pod.get_env("GRAYLOG_ELASTICSEARCH_HOSTS")):
        debuggy = Debuggy(namespace)
        debuggy.deploy()
        debuggy_pod = Pod(namespace, debuggy.get_name())
        cmd_str = [
            "curl",
            "-s",
            f"{os_conn_str}/_cluster/settings?include_defaults=true"
        ]
        response = debuggy_pod.exec(cmd_str)
        if response["status"] == "success":
            back_pressure_mode = "Unknown"
            os_settings = json.loads(response["output"])
            try:
                back_pressure_mode = os_settings["persistent"]["search_backpressure"]["mode"]
            except:
                back_pressure_mode = os_settings["defaults"]["search_backpressure"]["mode"]
            print(f"{namespace} -> search_backpressure.mode: {back_pressure_mode}")
            debuggy.destroy()
        else:
            print(response)
