#!/usr/bin/env python2
#-*- coding: utf8 -*-

import time
import subprocess
import shlex
import json
import sys

VERSION="0.1"

CMD_GETINFO="/root/safe_v2.0.0_linux/safe-cli getinfo"
CMD_GETTIPS="/root/safe_v2.0.0_linux/safe-cli getchaintips"
CMD_STOP="/root/safe_v2.0.0_linux/safe-cli stop"
CMD_START="/root/safe_v2.0.0_linux/safed"
CMD_RBJ_TMPL="/root/safe_v2.0.0_linux/safe-cli reconsiderblock %s "

def run_cmd_ret_output(cmd) :
    cmd = shlex.split(cmd)
    output = subprocess.check_output(cmd)
    return output

def run_cmd_ret_code(cmd) :
    cmd = shlex.split(cmd)
    code = subprocess.call(cmd)
    return code

def run_cmd_popen(cmd) :
    cmd = shlex.split(cmd)
    p = subprocess.Popen(cmd)
    return p

def run_getinfo():
    output = run_cmd_ret_output(CMD_GETINFO)
    return json.loads(output)

def run_gettips() :
    output = run_cmd_ret_output(CMD_GETTIPS)
    return json.loads(output)

def check(getinfo_result, gettips_result) : #return (bool, block_hash)
    blocks = getinfo_result['blocks']
    t = gettips_result[0]
    if t['status'] != 'invalid' :
        return (False, None)
    height = t['height']
    eq = (blocks + 1) == height
    block_hash = t['hash']
    return (eq, block_hash)

def run_stop():
    run_cmd_ret_code(CMD_STOP)

def rm_data_files():
    files = [
        '/root/.safe/governance.dat',
        '/root/.safe/mnpayments.dat',
        '/root/.safe/mncache.dat',
        '/root/.safe/peers.dat',
        '/root/.safe/banlist.dat',
    ]

    for f in files:
        cmd = "rm -rf %s" % f
        print cmd
        run_cmd_ret_code(cmd)

def safe_sleep(total, interval=1):
    tt = time.time()
    while True :
        time.sleep(interval)
        ttt = time.time()
        if abs(ttt - tt) >= total :
            return
        else :
            pass

def fork_start() :
    cmd = CMD_START
    print cmd
    p = run_cmd_popen(cmd)
    return p

def run_rbj(block_hash) :
    cmd = CMD_RBJ_TMPL % block_hash
    print cmd
    run_cmd_ret_code(cmd)

def main():
    getinfo_result = run_getinfo()
    gettips_result = run_gettips()
    ret, block_hash = check(getinfo_result, gettips_result)
    if not ret:
        print "看起来不像是区块卡住，请自行确认；程序退出"
        sys.exit(0)

    print "看起来像是区块卡住，将进行修复"
    print "step 1: run_stop(); safe_sleep(1) #关闭节点程序"
    run_stop(); safe_sleep(1)
   
    print '-' * 40 
    print "step 2: rm_data_files() #删除数据文件"
    rm_data_files()

    print '-' * 40 
    print "step 3: p = fork_start(); safe_sleep(36) #启动节点程序，等待30秒左右"
    p = fork_start(); safe_sleep(36)

    print '-' * 40 
    print "step 4: run_rbj(block_hash); safe_sleep(3) #重置区块高度"
    run_rbj(block_hash); safe_sleep(3)

    print '-' * 40 
    print "step 5: run_stop(); safe_sleep(10) #关闭节点程序，等待10秒"
    run_stop(); safe_sleep(10)

    print '-' * 40 
    print "step 6: p = fork_start(); safe_sleep(36) #启动节点程序，等待30秒左右"
    p = fork_start(); safe_sleep(36)

    print '-' * 40 
    print "step 7: getinfo_result = run_getinfo() #重新查看区块高度"
    blocks_bf = getinfo_result['blocks']
    getinfo_result = run_getinfo()
    blocks_af = getinfo_result['blocks']
    print '-' * 60 
    print 'blocks: before = %s, after = %s' % (blocks_bf, blocks_af)
    print getinfo_result

if __name__ == '__main__':
    main()
