# nix develop .#t1.elaborator

#configs="blastoise machamp sandslash alakazam"
# configs="blastoise machamp sandslash"
# configs="blastoise sandslash"
configs="blastoise"

configsPath=configs
resultPath=result
baseResult=master_res
gen_configs="true"
# run_configs="true"
#diff_master="true"

if [ "$gen_configs" == "true" ]; then
    for c in $configs
    do
        mill configgen $c -t $configsPath
        # mv $configsPath $c.json
    done
fi

if [ "$run_configs" == "true" ]; then
    for c in $configs
    do
    {
        rm -rf $resultPath\_$c
        mkdir -p $resultPath\_$c
        mill --no-server elaborator ipemu -t $resultPath\_$c -c $c.json 2>&1 | tee  $resultPath\_$c/run.log
    }&
    done
fi

if [ "$diff_master" == "true" ]; then
    for c in $configs
    do
        diff $resultPath\_$c/run.log $baseResult\/$resultPath\_$c/run.log
        echo "diff" $resultPath\_$c/run.log $baseResult\/$resultPath\_$c/run.log
    done
fi

<<printcode
    val newOps = ops(fpuEnable)
    val newAll = all(fpuEnable)
    val out = new DecodeTable[Op](newOps, all(fpuEnable))
    println("testing")
    newOps.map{ 
      op => 
        print(op.bitPat, op.tpe, op.funct6, op.tpeOp2,  op.funct3, op.name,  op.special, op.notLSU) 
        // print(op.bitPat.toString().substring(0,27), op.tpe, op.funct6, op.tpeOp2,  op.funct3, op.name,  op.special, op.notLSU) 
        out.table.table.map {
          tb => 
            if(tb._1 == op.bitPat)
              println(tb._2)  
        }
    }
    println("testingend")
    out
printcode

