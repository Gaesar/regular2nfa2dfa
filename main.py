from regular2nfa2dfa import Regular2nfa2dfa

if __name__ == '__main__':
    regular_express = "(a|b)*a(a|b)"
    # "(a|b|ε)*(a|b*)"
    # "(a*|b*)b(ba)*"
    # "a*(a|b)a(a|b)*"
    # "(a|b)*a(a|b)"
    # "ab|c(d*|a)"
    # “(a|b)*a(a|b)*”
    g = Regular2nfa2dfa(regular_express)
    g.draw_nfa()
    g.draw_dfa()
    g.draw_and_simplify_dfa()
    print(g.match("bbaabbaabb"))

