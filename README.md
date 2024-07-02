# 正则表达式转NFA转DFA转最小DFA

## 项目依赖

需要下载安装graphviz。

## 项目目录

```
regular2nfa2dfa
|-main.py # 程序入口
|-README.md 
|-regular2nfa2dfa.py # 实现的所有算法
```

## 运行程序

运行main.py即可运行程序。

```python
if __name__ == '__main__':
    regular_express = "(a|b)*a(a|b)"  # 填写正则表达式，支持·、|、*、ε
    # 正则表达式示例：
    # "(a|b|ε)*(a|b*)"       
    # "(a*|b*)b(ba)*"
    # "a*(a|b)a(a|b)*"
    # "(a|b)*a(a|b)"
    # "ab|c(d*|a)"
    # “(a|b)*a(a|b)*”
    g = Regular2nfa2dfa(regular_express)  # 通过正则表达式构造对象
    g.draw_nfa()  # 调用draw_nfa()方法，可以绘制nfa
    g.draw_dfa()  # 调用draw_dfa()方法，可以绘制dfa
    g.draw_and_simplify_dfa()  # 调用draw_and_simplify_dfa()方法可以绘制最小dfa
    print(g.match("bbaabbaabb"))  # 调用match()方法可以匹配字符串，判断是否符合正则表达式
```

## 结果展示

regular_express 填写为 (a|b)*a(a|b)

运行后会自动绘制并打开3张图片，依次为NFA、DFA、最小DFA

![NFA.gv](https://cdn.jsdelivr.net/gh/Gaesar/Gaesar.github.io@main/pic/202407021323151.png)

​											            NFA.gv.png

![DFA.gv](https://cdn.jsdelivr.net/gh/Gaesar/Gaesar.github.io@main/pic/202407021323519.png)

​														DFA.gv.png![DFAs.gv](https://cdn.jsdelivr.net/gh/Gaesar/Gaesar.github.io@main/pic/202407021323769.png)

​														DFAs.gv.png