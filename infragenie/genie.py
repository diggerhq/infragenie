import os
import json
import glob
import shutil
from pathlib import Path
import subprocess
from rich import print
import hcl2


def construct_dag():
    pass


def parsetform(path):
    res = {}
    for filename in glob.glob(os.path.join(path, "*.tf")):
        with open(filename, "r") as f:
            d = hcl2.load(f)
            res.update(d)
    return res


def genVars(path, variables):
    with open(os.path.join(path, "genie_variables.tf"), "a") as f:
        for key, val in variables.items():
            f.write(f"""
variable "{key}" {{
    default = "{val}"
}}
""")

def genInputs(path, data, injects, resolved_outputs):
    with open(os.path.join(path, "genie_inputs.tf"), "a") as f:
        for output in resolved_outputs:
            t = output["type"]
            n = output["name"]
            rn = output["resource_name"]
            output_id = output["id"]
            f.write(f"""
data "{t}" "{n}" {{
    id = "{output_id}"
}}

    """)

def genoutputs(path, resources, injects):
    outputs = []
    with open(os.path.join(path, "genie_outputs.tf"), "a") as f:
        resource_names = list(map(lambda x: x["resource_name"], injects))
        names = list(map(lambda x: x["name"], injects))
        types = list(map(lambda x: x["type"], injects))

        for i in range(len(injects)):
            t = types[i]
            rn = resource_names[i]
            n = names[i]
            if rn in resources.get(t, []):
                outputs.append({
                    "resource_name": rn,
                    "name": n,
                    "type": t
                })
                f.write(f"""
output "{rn}_id"{{
    value = {t}.{rn}.id
}}
    
""")
    return outputs

def applyAndResolveOutputs(path, outputs, pipelineName):
    cdir = os.getcwd()
    os.chdir(path)
    subprocess.run(["terraform", "init"], check=True)
    subprocess.run(["terraform", "apply", "-state", f"../../{pipelineName}.terraform.tfstate"], check=True)
    proc = subprocess.run(["terraform", "output", "-json", "-state", f"../../{pipelineName}.terraform.tfstate"], capture_output=True)
    terraform_outputs = proc.stdout.decode("utf-8").strip()
    terraform_outputs = json.loads(terraform_outputs)
    resolved = []
    for output in outputs:
        n = output["name"]
        rn = output["resource_name"]
        t = output["type"]
        resolved.append({
            "id": terraform_outputs[f"{rn}_id"]["value"],
            "type": t,
            "name": n,
            "resource_name": rn,
        })

    os.chdir(cdir)
    return resolved

def cli():
    print(":vampire: welcome to [bold magenta]InfraGenie[/bold magenta] CLI! :smile:")

    print("parsing genie.hcl file ...")

    with open("genie.hcl") as f:
        d = hcl2.load(f)
        print("found the following settings:")
        print(d)
        globalVars = d.get("variables", [{}])[0]

    print("Rendering data outputs")
    injects = []
    for name, inject in d["inject"][0].items():
        source = inject["source"].replace("${", "").replace("}", "")
        print(name, source)
        module, rtype, rname, = source.split(".")
        injects.append({
            "name": name,
            "module": module,
            "type": rtype,
            "resource_name": rname
        })

    print("rendering terraform outputs")

    shutil.rmtree(".infragenie")
    Path(".infragenie").mkdir(parents=True, exist_ok=True)
    resolved_outputs = []
    for pipeline in d["pipeline"][0]["steps"]:
        if "source" in pipeline:
            pipelinename, pipelinesource = pipeline["name"], pipeline.get("source")

            modulePath = os.path.join(f".infragenie/{pipeline['name']}")
            shutil.copytree(pipeline["source"], modulePath)

            tformdata = parsetform(modulePath)
            print(tformdata)
            tformRequires = tformdata.get("data", [{}])[0]
            terraformResources = tformdata.get("resource", [{}])[0]
            terraformResources.keys()

            genVars(modulePath, globalVars)
            genInputs(modulePath, tformRequires, injects, resolved_outputs)
            outputs = genoutputs(modulePath, terraformResources, injects)

            
            tmpOutputs = applyAndResolveOutputs(modulePath, outputs, pipelinename)
            resolved_outputs.extend(tmpOutputs)

