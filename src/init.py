import json

import utils


def process_files(init):
    out = {}
    for f in init["files"]:
        h = utils.calc_hash(f["content"])
        out[h] = f["content"]
    for p in init["programs"]:
        h = utils.calc_hash(p["content"])
        out[h] = p["content"]
    for f in init["functions"]:
        h = utils.calc_hash(p["content"])
        out[h] = f

    out = {
        k: {"content": v, "when_modified": [utils.get_time()], "when_accessed": []}
        for k, v in out.items()
    }

    return out


def process_programs(init):
    programs = {}
    for p in init["programs"]:
        content = p.pop("content")
        programs[p["name"]] = utils.calc_hash(content)
    for k, v in init["system_functions"].items():
        programs[k] = utils.calc_hash(v)
    return programs


def process_system(init):
    out = {}
    for k, v in init["system_functions"].items():
        out[utils.calc_hash(v)] = v
    return out


def process_permissions(init):
    out = {}
    for p in init["programs"]:
        out[p["name"]] = {
            "network (incoming)": False,
            "network (outgoing)": False,
            "file (read)": True,
            "file (write)": False,
        }
    return out


def parse():
    with open("./src/init.json", "r") as f:
        init = json.load(f)

    data = {
        "files": process_files(init),
        "programs": process_programs(init),
        "system": process_system(init),
        "permissions": process_permissions(init),
    }

    return data
