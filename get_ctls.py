import os

logs = "log/${ctl}.log"
scala_f = "log/scala/${ctl}.scala"
cmd = "rg ${ctl} run.log  | sort | uniq > " + logs
ctls_map = {
    "logic": "Instruction should use [[org.chipsalliance.t1.rtl.decoder.TableGenerator.LaneDecodeTable.LogicUnit]].",
    "adder": "goes to [[org.chipsalliance.t1.rtl.LaneAdder]].",
    "shift": "goes to [[org.chipsalliance.t1.rtl.LaneShifter]].",
    "multiplier": "goes to [[org.chipsalliance.t1.rtl.LaneMul]]. (only apply to int mul)",
    "divider": "goes to [[org.chipsalliance.t1.rtl.LaneDiv]] or [[org.chipsalliance.t1.rtl.LaneDivFP]]. if FP exist, all div goes to [[org.chipsalliance.t1.rtl.LaneDivFP]]",
    "multiCycle": "TODO: remove? only Div or customer",
    "other": "goes to [[org.chipsalliance.t1.rtl.OtherUnit]]",
    "floatType": "is a float type. TODO: remove it.",
    "float": "goes to [[org.chipsalliance.t1.rtl.LaneFloat]].",
    "floatConvertUnsigned": "TODO: remove it.",
    "FMA": "uop of FMA, goes to [[org.chipsalliance.t1.rtl.LaneFloat]] FMA unit.",
    "floatMul": "TODO: add op.",
    "orderReduce": "don't use it, it's slow, lane read all elements from VRF, send to Top.",
    "FDiv": "todo: remove FDiv",
    "FCompare": "TODO: remove it, but remains attribute.",
    "FOther": "designed for Other Unit in FP. goes to [[org.chipsalliance.t1.rtl.LaneFloat]] OtherUnit. TODO: perf it.",
    "firstWiden": "There are two types of widen: - vd -> widen. - vs2, vd -> widen. This op will widen vs2. TODO: remove it as attribute.",
    "nr": "for vmvnr, move vreg group to another vreg group.  it will ignore lmul, use from instr.  chainable",
    "red": """do reduce in each lane.
each element will sequentially executed in each lanes.
after finishing, pop it to Top, and use ALU at top to get the final result and send to element0
TODO: better name.
""",
    "maskOp": "TODO: remove this.",
    "reverse": """only instruction will switch src.
TODO: send it to uop.
""",
    "narrow": """
dual width of src will be convert to single width to dst.
narrow can be the src of chain.
as the dst of chain, only can be fed with Load.
TODO: remove it as attribute.
""",
    "crossWrite": "lane should write to another lane",
    "widenReduce": """a special widen, only write dual vd from Top to element0
it doesn't cross.
TODO: better name.
""",
    "saturate": """For adder, does it need to take care of saturate.
TODO: add to uop
""",
    "average": """For adder, does it need to take care of saturate.
TODO: add to uop
""",
    "unsigned0": """is src0 unsigned?
used everywhere in Lane and VFU.
""",
    "unsigned1": """
is src1 unsigned?
used everywhere in Lane and VFU.
""",
    "vtype": "src1 is vtype.",
    "itype": "src is imm.",
    "targetRd": "write rd/fd at scalar core.",
    "extend": "send element to MaskUnit at top, extend and broadcast to multiple Lanes.",
    "mv": """move instruction, v->v s->v x->v,
single element move.
TODO: split them into multiple op since datapath differs
""",
    "ffo": """find first one,
lane will report if 1 is found, Sequencer should decide which is exactly the first 1 in lanes.
after 1 is found, tell each lane, 1 has been found at which the corresponding location.
lane will stale at stage2.
TODO: should split into lane control uop
""",
    "slid": """used in Sequencer mask unit, decide which vrf should be read.
send read request to corresponding lane, lane will respond data to Sequencer.
Sequencer will write data to VD.
mask unit is work as the router here.
TODO: opimize mask unit.
""",
    "gather": """lane will read index from vs1, send to Sequencer.
mask unit will calculate vrf address based on the vs1 from lane, and send read request to lanes,
lanes should read it and send vs2 to Sequencer.
Sequencer will write vd at last.
address: 0 -> vlmax(sew decide address width.)
""",
    "gather16": """same with [[gather]]
ignore sew, address width is fixed to 16.
@note
When SEW=8, vrgather.vv can only reference vector elements 0-255.
The vrgatherei16 form can index 64K elements,
and can also be used to reduce the register capacity needed to hold indices when SEW > 16.
""",
    "compress": """lane will read data from vs2, send to Sequencer.
then Sequencer will read vs1 for mask.
use mask to compress data in vs2.
and write to vd at last.
""",
    "readOnly": """lane read only instructions.
for these instructions lane will only read vrf and send data back to Sequencer. """,
    "popCount": """
count how many 1s in VS2.
lane will use [[org.chipsalliance.t1.rtl.OtherUnit]] to how many 1s locally;
use reduce datapath to accumulate,
send total result to top
top will send result to vd.
""",
    "iota": """lane will read vs2 from VRF, send to Top.
Top read v0(at register) calculate the result and write back to VRFs
""",
    "id": """write 0...vlmax to VRF.
Lane other unit should handle it.
TODO: remove it, it's a uop.
""",
    "vwmacc": """special MAC instruction, MAC use vd as source, it cross read vd.
TODO: cross read vd + mac uop.
""",
    "unOrderWrite": """unmanaged write for VRF. these instructions cannot be chain as source.
TODO: add an attribute these instruction cannot be the source of chaining.
""",
    "maskLogic": """only one or two operators
src is mask format(one element one bit).
vl should align with src.
if datapath is unaligned, need to take care the tail.
""",
    "maskDestination": """vd is mask format.
execute at lane, send result to Sequencer, regroup it and write to vd.
if datapath is unaligned, need to take care the tail.
""",
    "maskSource": """three ops. these ops don't use mask. use v0 as third op, read it from duplicate V0.
it will read
use mask(v0) in mask format as source.
""",
    "indexType": "TODO: remove it.",
    "special": """if Sequencer is the router for data from Lane to LSU or Sequencer mask unit.
special -> maskUnit || index type load store
""",
    "maskUnit": """mask unit -> red || compress || viota || ffo || slid || maskDestination || gather(v) || mv || popCount || extend
all instruction in Sequencer mask unit. """,
    "crossRead": """Read vs2 or vd with cross read channel.
crossRead -> narrow || firstWiden
""",
    "sWrite": """sWrite -> targetRd || readOnly || crossWrite || maskDestination || reduce || loadStore
instruction will write vd or rd(scalar) from outside of lane.
It will request vrf wait, and lane will not write.
""",
    "ma": """decodeResult(Decoder.multiplier) && decodeResult(Decoder.uop)(1, 0).xorR && !decodeResult(Decoder.vwmacc)
TODO: remove it. */
""",
    "sReadVD": """sReadVD -> !(ma || maskLogic)
instruction need to read vd as operator.
""",
    "scheduler": """wScheduler 原来与 sScheduler 如果出错了需要检查一下,真不一样需要说明记录
sScheduler -> maskDestination || red || readOnly || ffo || popCount || loadStore
lane will send request to Sequencer and wait ack from Sequencer. */
""",
    "dontNeedExecuteInLane": """sExecute 与 wExecuteRes 也不一样,需要校验
sExecute -> readOnly || nr || loadStore
Lane doesn't need VFU to execute the instruction.
datapath will directly goes to VRF.
    """,
    "specialSlot": """lane中只能在slot0中执行的指令
specialSlot -> crossRead || crossWrite || maskLogic || maskDestination || maskSource
instructions schedule to slot0.
    """,
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
