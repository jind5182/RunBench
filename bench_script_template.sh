sysbench --test=cpu run --num-threads=1 --max-requests=20000 --percentile=98 --cpu-max-prime=10000
sysbench --test=cpu run --num-threads=xxxxx --max-requests=20000 --percentile=98 --cpu-max-prime=10000

sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=seqrd --file-total-size=2G --file-block-size=16384 --file-num=128 prepare
sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=seqrd --file-total-size=2G --file-block-size=16384 --file-num=128 run
sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=seqrd --file-total-size=2G --file-block-size=16384 --file-num=128 cleanup

sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=seqwr --file-total-size=2G --file-block-size=16384 --file-num=128 prepare
sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=seqwr --file-total-size=2G --file-block-size=16384 --file-num=128 run
sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=seqwr --file-total-size=2G --file-block-size=16384 --file-num=128 cleanup

sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=rndrd --file-total-size=2G --file-block-size=16384 --file-num=128 prepare
sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=rndrd --file-total-size=2G --file-block-size=16384 --file-num=128 run
sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=rndrd --file-total-size=2G --file-block-size=16384 --file-num=128 cleanup

sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=rndwr --file-total-size=2G --file-block-size=16384 --file-num=128 prepare
sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=rndwr --file-total-size=2G --file-block-size=16384 --file-num=128 run
sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=rndwr --file-total-size=2G --file-block-size=16384 --file-num=128 cleanup

sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=rndrw --file-total-size=2G --file-block-size=16384 --file-num=128 prepare
sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=rndrw --file-total-size=2G --file-block-size=16384 --file-num=128 run
sysbench --test=fileio --num-threads=1 --max-requests=20000 --percentile=98 --file-test-mode=rndrw --file-total-size=2G --file-block-size=16384 --file-num=128 cleanup

sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=seqrd --file-total-size=2G --file-block-size=16384 --file-num=128 prepare
sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=seqrd --file-total-size=2G --file-block-size=16384 --file-num=128 run
sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=seqrd --file-total-size=2G --file-block-size=16384 --file-num=128 cleanup

sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=seqwr --file-total-size=2G --file-block-size=16384 --file-num=128 prepare
sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=seqwr --file-total-size=2G --file-block-size=16384 --file-num=128 run
sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=seqwr --file-total-size=2G --file-block-size=16384 --file-num=128 cleanup

sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=rndrd --file-total-size=2G --file-block-size=16384 --file-num=128 prepare
sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=rndrd --file-total-size=2G --file-block-size=16384 --file-num=128 run
sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=rndrd --file-total-size=2G --file-block-size=16384 --file-num=128 cleanup

sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=rndwr --file-total-size=2G --file-block-size=16384 --file-num=128 prepare
sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=rndwr --file-total-size=2G --file-block-size=16384 --file-num=128 run
sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=rndwr --file-total-size=2G --file-block-size=16384 --file-num=128 cleanup

sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=rndrw --file-total-size=2G --file-block-size=16384 --file-num=128 prepare
sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=rndrw --file-total-size=2G --file-block-size=16384 --file-num=128 run
sysbench --test=fileio --num-threads=xxxxx --max-requests=20000 --percentile=98 --file-test-mode=rndrw --file-total-size=2G --file-block-size=16384 --file-num=128 cleanup

sysbench --test=memory run --num-threads=1 --percentile=98 --memory-total-size=100G --memory-block-size=1K --memory-oper=read
sysbench --test=memory run --num-threads=1 --percentile=98 --memory-total-size=100G --memory-block-size=1K --memory-oper=write
sysbench --test=memory run --num-threads=xxxxx --percentile=98 --memory-total-size=100G --memory-block-size=1K --memory-oper=read
sysbench --test=memory run --num-threads=xxxxx --percentile=98 --memory-total-size=100G --memory-block-size=1K --memory-oper=write