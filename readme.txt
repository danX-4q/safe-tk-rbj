
1. how to execute
chmod +x *
./safe-tk-rbj.py

====================================

2. how to set env var

vi ./safe-tk-rbj.py
reset the value of vars, if necessary
    CMD_GETINFO
    CMD_GETTIPS
    CMD_STOP
    CMD_START
    CMD_RBJ_TMPL

!specially, and check *files* in function rm_data_files()

