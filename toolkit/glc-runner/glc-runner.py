#!/usr/bin/env python3

from _lib.cmd import Cmd
from _lib.converter import JsonConverter
from _lib.k8s import K8S, Debuggy, Pod

k8s = K8S()
json = JsonConverter()
cmd = Cmd()

tenant_ns_list = k8s.get_namespaces(filter="^tenant-.*")

for namespace in tenant_ns_list:
    tenant_name = namespace.replace("tenant-", "")

    admin_token = k8s.get_secret(
        namespace, f"glc-tenant-state-{tenant_name}", "graylog_admin_token"
    )
    if admin_token is not None:
        cmd_str = [
            "curl",
            "-k",
            "-u",
            f"{admin_token}:token",
            "-H",
            "Content-type: application/json",
            f"https://{tenant_name}.graylog.cloud/api/system/cluster/traffic?daily=true&days=2",
        ]
        response = cmd.run(cmd_str)
        pretty_json = json.pretty(response["stdout"])
        if pretty_json is not None:
            print("-----===== --------------------------------------- =====-----")
            print(f"Tenant name: {tenant_name}")
            print(f"Tenant URL: https://{tenant_name}.graylog.cloud")
            print("-----===== --------------------------------------- =====-----")
            print(pretty_json)
            print("\n\n")
    # graylog_pod = Pod(namespace, "graylog-application-0")
    # if (os_conn_str := graylog_pod.get_env("GRAYLOG_ELASTICSEARCH_HOSTS")):
    #     debuggy = Debuggy(namespace)
    #     debuggy.deploy()
    #     debuggy_pod = Pod(namespace, debuggy.get_name())
    #     cmd_str = [
    #         "curl",
    #         "-s",
    #         f"{os_conn_str}/_cluster/settings?include_defaults=true"
    #     ]
    #     response = debuggy_pod.exec(cmd_str)
    #     if response["status"] == "success":
    #         back_pressure_mode = "Unknown"
    #         os_settings = json.loads(response["output"])
    #         try:
    #             back_pressure_mode = os_settings["persistent"]["search_backpressure"]["mode"]
    #         except:
    #             back_pressure_mode = os_settings["defaults"]["search_backpressure"]["mode"]
    #         print(f"{namespace} -> search_backpressure.mode: {back_pressure_mode}")
    #         debuggy.destroy()
    #     else:
    #         print(response)
