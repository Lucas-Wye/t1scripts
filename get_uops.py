import os

logs = "log/${ctl}.log"
scala_f = "log/scala/${ctl}.scala"
cmd = "rg ${ctl} run.log  | sort | uniq > " + logs
ctls_map = {
    "topuopUp": "up", 
    "topuopSlid1": "slid1",
    "topuopSignExtend": "signExtend",
}
ctls = ctls_map.keys()


def gen_data_n(instrs, exist_instrs):
    nonexist_instr = []
    for i in instrs:
        if i not in exist_instrs:
            nonexist_instr.append(i)
    return nonexist_instr

def remove_same(instr):
    return list(set(instr))

with open("ctrl_template.txt", "r") as f:
    scala_w = f.read()

all_instr = []
# get all instr first
for ctl in ctls:
    os.system(cmd.replace("${ctl}", ctl))
    with open(logs.replace("${ctl}", ctl), "r") as file:
        data = file.read().split("\n")
        if len(data) > 0:
            for _d in data:
                if len(_d) > 0 and _d[0] == "(" and _d[-1] == ")":
                    t = _d.split(",")
                    if len(t) == 2:
                        t = t[1].replace(")", "").strip()
                        if t not in all_instr:
                            all_instr.append(t)
print(all_instr)

# gen scala code
for ctl in ctls:
    with open(logs.replace("${ctl}", ctl), "r") as file:
        data = file.read().split("\n")
        if len(data) > 0:
            out_d = []
            for _d in data:
                if len(_d) > 0 and _d[0] == "(" and _d[-1] == ")":
                    t = _d.split(",")
                    if len(t) == 2:
                        t = t[1].replace(")", "").strip()
                        out_d.append(t)
                    else:
                        # print(t)
                        pass
            out_d = remove_same(out_d.copy())
            out_d.sort()
            if len(out_d) > 0:
                with open(
                    scala_f.replace("${ctl}", "is" + ctl.capitalize()),
                    "w",
                ) as wfile:
                    data_s = "Seq(\n"
                    data_e = "\n    )"
                    if 'float' in ctl:
                        data_s = "if(t1DecodePattern.t1Parameter.fpuEnable) Seq(\n"
                        data_e = "\n    ) else Seq()"
                    _s = scala_w.replace(
                        "${data}", data_s + "\n".join('      "' + _d + '",' for _d in out_d) + data_e
                    )
                    out_dn = remove_same(gen_data_n(all_instr, out_d))
                    out_dn.sort()
                    _s = _s.replace(
                        "${data_n}", "\n".join('      "' + _d + '",' for _d in out_dn)
                    )
                    _s = _s.replace("${ctl}", ctl.capitalize())
                    _s = _s.replace("${comment}", ctls_map[ctl].replace("\n"," "))
                    wfile.write(_s)
            else:
                print(f"empty attribute: {ctl}")
