## 安装
1. 只支持WINDOWS平台
2. 安装Syvod。以下假设安装到目录C:\Syvod
3. 运行Syvod\VODManager登录VOD系统并配置。运行Syvod\Syvod确定系统能正常运行
4. 安装GIT PYTHON3 PIP，注意在PATH环境中加入对应二进制目录
5. 运行 `pip install aiohttp pyodbc` 安装依赖模块
6. 在C:\Syvod目录下执行 `git clone https://github.com/juliuswwj/syweb`
7. 运行syweb\main.py
8. 在手机上访问网站 `http://IP` IP是VOD系统的内部IP

## SY protocol @ 7888
1. status
    S->C 
        3f 2c 31 2c 30 2c 35 30 3c 3e                     ?,1,0,50<>
    1st number is track
    2nd number is pause 
    3rd number is volume

2. echo
    S->C
        7e 31 32 33 34 35 3c 3e                           ~12345<>
    C->S
        3b 31 32 33 34 35 3c 3e 0a                        ;12345<>.

3. current play list
    S->C
        24 2c 31 30 30 30 30 38 7c 7c e5 8d 81 e5 b9 b4   $,100008||......
        7c 7c e9 99 88 e5 a5 95 e8 bf 85 7c 7c 30 7c 7c   ||.........||0||
        30 7c 7c 31 30 30 30 31 34 7c 7c e8 af bb e4 bd   0||100014||.....
        a0 7c 7c e9 99 88 e6 b7 91 e6 a1 a6 5f e6 9d 8e   .||........._...
        e5 ae 97 e7 9b 9b 7c 7c 30 7c 7c 30 7c 7c 3c 3e   ......||0||0||<>

4. data
    C->S
        7e 30 3c 3e 0a                                    ~0<>.
    S->C
        25 31 30 30 30 30 31 7c 7c e6 88 90 e9 83 bd 7c   %100001||......|
        7c e8 b5 b5 e9 9b b7 7c 7c 30 7c 7c 30 7c 7c 7c   |......||0||0|||
        7c 32 7c 7c 43 44 7c 7c 31 37 37 39 7c 7c 30 7c   |2||CD||1779||0|
        7c 7c 7c 32 30 30 30 2d 30 31 2d 30 31 3f 3f 31   |||2000-01-01??1
        3c 3e                                             <>
    C->S
        7e 30 3c 3e 0a                                    ~0<>.
    S->C
        25 31 30 30 30 30 33 7c 7c e5 90 8e e6 9d a5 7c   %100003||......|
        7c e5 88 98 e8 8b a5 e8 8b b1 7c 7c 30 7c 7c 30   |.........||0||0
        7c 7c 7c 7c 32 7c 7c 48 4c 7c 7c 31 33 34 35 7c   ||||2||HL||1345|
        7c 31 7c 7c 7c 7c 32 30 30 30 2d 30 31 2d 30 31   |1||||2000-01-01
        ...
        7c 32 30 30 30 2d 30 31 2d 30 31 3f 3f 30 3c 3e   |2000-01-01??0<>
    C->S
        5e 73 69 6e 67 65 72 3c 3e 0a                     ^singer<>.
    S->C
        26 e4 b9 94 e6 b4 8b 7c 7c 30 7c 7c e7 94 b7 7c   &......||0||...|
        7c 51 59 7c 7c 30 7c 7c e4 b9 94 e6 b4 8b 2e 6a   |QY||0||.......j
        70 67 3f 3f e4 ba 94 e8 89 b2 e7 9f b3 e5 8d 97   pg??............
        e5 8f b6 7c 7c 30 7c 7c e7 94 b7 7c 7c 57 53 53   ...||0||...||WSS
        ...
        31 31 7c 7c e5 88 98 e5 be b7 e5 8d 8e 2e 6a 70   11||..........jp
        67 3f 3f 3c 3e                                    g??<>

5. play a song
    C->S
        2a 2c 31 30 30 30 31 33 3c 3e 0a                  *,100013<>.
    S->C return current play list

6. control
    C->S
        3f 2c 46 3c 3e 0a                                 ?,F<>.
    the 3rd chararcter is command
    A: sound track
    B: pause
    C: next
    D: VOLUME+
    E: VOLUME-
    F: replay
    H: thumb up
    I: heart
    J: thumb down
    K: ignore

7. top
    C->S
        2b 2c 32 3c 3e 0a                                 +,2<>.

8. remove
    C->S
        2d 2c 31 3c 3e 0a                                 -,1<>.

9. download
    C->S
        44 2c 36 30 31 36 32 34 34 38 3c 3e 0a            D,60162448<>.
    S->C
        41 2c 31 30 30 30 31 38 7c 7c e6 88 91 e4 bb ac   A,100018||......
        e4 b8 8d e4 b8 80 e6 a0 b7 7c 7c e5 a4 a7 e5 a3   .........||.....
        ae 7c 7c 30 7c 7c 30 7c 7c 7c 7c 35 7c 7c 57 4d   .||0||0||||5||WM
        42 59 59 7c 7c 30 7c 7c 30 7c 7c 7c 7c 32 30 30   BYY||0||0||||200
        30 2d 30 31 2d 30 31 7c 7c 3c 3e                  0-01-01||<>
    



