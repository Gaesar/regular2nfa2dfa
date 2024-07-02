from graphviz import Digraph


class Regular2nfa2dfa:

    def __init__(self, regular_express):
        suffix_express = self.__get_suffix_express(regular_express)
        self.__start, self.__end, self.__edges, self.__char_set = self.__get_nfa(suffix_express)
        self.__size = self.__end + 1
        self.__graph = self.__edge2graph(self.__edges, self.__size)
        self.__epsilon_close_map = self.__get_all_epsilon_close()
        self.__current_no = None
        self.__state_transition_table = None

    def __get_regular_as_list(self, regular_express):
        """
        :param regular_express: 正则表达式
        :return: 添加·后的字符列表
        """
        regular_express_list = [char for char in regular_express]
        regular_list = []
        regular_list.append(regular_express_list[0])
        for i in range(1, len(regular_express_list)):
            # ab、a(、)a、)(、*(、*a
            if (regular_express_list[i].isalpha() and regular_express_list[i - 1].isalpha()) or \
                    (regular_express_list[i] == '(' and regular_express_list[i - 1].isalpha()) or \
                    (regular_express_list[i].isalpha() and regular_express_list[i - 1] == ')') or \
                    (regular_express_list[i] == '(' and regular_express_list[i - 1] == ')') or \
                    (regular_express_list[i] == '(' and regular_express_list[i - 1] == '*') or \
                    (regular_express_list[i].isalpha() and regular_express_list[i - 1] == '*'):
                regular_list.append('·')
            regular_list.append(regular_express_list[i])
        return regular_list

    def __get_suffix_express(self, regular_express):
        """
        正则表达式-->后缀表达式
        :param regular_express: 正则表达式
        :return: 后缀表达式
        """
        regular_list = self.__get_regular_as_list(regular_express)
        priority = {'|': 0, '·': 1, '*': 2}
        stack = []
        suffix_express = []
        for char in regular_list:
            if char.isalpha():
                suffix_express.append(char)
            elif char == '(':
                stack.append(char)
            elif char == ')':
                while stack[-1] != '(':
                    suffix_express.append(stack.pop())
                stack.pop()
            else:
                while len(stack) != 0 and stack[-1] != '(' and priority[char] <= priority[stack[-1]]:
                    suffix_express.append(stack.pop())
                stack.append(char)
        while len(stack) != 0:
            suffix_express.append(stack.pop())
        return suffix_express

    def __get_nfa(self, suffix_express):
        """
        使用正推的方法求出nfa
        :param suffix_express: 后缀表达式
        :return:  初始状态，终止状态，nfa的边集，字母集
        """
        index = 0  # 编号
        edges = []
        state_stack = []  #
        char_set = []
        for char in suffix_express:
            if char.isalpha() or char == 'ε':
                edges.append([index, char, index + 1])
                if char != 'ε' and char not in char_set:
                    char_set.append(char)
            elif char == '·':
                state2 = state_stack.pop()
                state1 = state_stack.pop()
                edges.append([state1[-1], 'ε', state2[0]])
                edges.append([index, 'ε', state1[0]])
                edges.append([state2[-1], 'ε', index + 1])
            elif char == '|':
                state2 = state_stack.pop()
                state1 = state_stack.pop()
                edges.append([index, 'ε', state1[0]])
                edges.append([index, 'ε', state2[0]])
                edges.append([state1[-1], 'ε', index + 1])
                edges.append([state2[-1], 'ε', index + 1])
            elif char == '*':
                state = state_stack.pop()
                edges.append([state[-1], 'ε', state[0]])
                edges.append([index, 'ε', state[0]])
                edges.append([state[-1], 'ε', index + 1])
                edges.append([index, 'ε', index + 1])
            state_stack.append([index, index + 1])
            index += 2
        start = state_stack[0][0]
        end = state_stack[0][1]
        edges.sort(key=lambda x: x[0])
        return start, end, edges, char_set

    def __edge2graph(self, edges, size):
        """
        以二维数组表示nfa
        :param edges: 边集
        :param size:  结点的个数
        :return:  二维数组表示的nfa
        """
        graph = [['0'] * size for _ in range(size)]
        for edge in edges:
            graph[int(edge[0])][int(edge[-1])] = edge[1]
        return graph

    def __get_all_epsilon_close(self):
        """
        求出所有结点的epsilon闭包
        :param graph: 二维数组表示的nfa
        :return:  epsilon_map: 结点对应的epsilon闭包的映射
        """

        def epsilon_close(t, visited):
            """
            递归求单个结点的epsilon闭包
            :param t:  结点编号
            :param visited:  记录路径上已经访问过的点，防止出现循环
            :return: 单个结点的epsilon闭包
            """
            visited[t] = True
            ret = set()
            for i in range(len(self.__graph[t])):
                if self.__graph[t][i] == 'ε' and visited[i] == False:
                    ret = ret | epsilon_close(i, visited)
            ret.add(t)
            visited[t] = False
            return ret

        size = len(self.__graph)
        epsilon_map = dict()
        visited = [False for _ in range(size)]
        for sta in range(size):
            epsilon_map[sta] = epsilon_close(sta, visited)
        return epsilon_map

    def __get_dfa(self):
        """
        根据nfa求dfa、最简dfa
        :param start: 初始状态
        :param end: 终止状态
        :param graph: 二维数组表示的nfa
        :param char_set:  字母集
        :param map: 所有结点epsilon闭包的映射
        :return: dfa结点与简化dfa结点之间的映射，起始状态，终止状态集，dfa边集，简化dfa边集
        """
        dfa = []  # dfa的边集
        state_transition_table = []  # dfa的状态转换表
        cur_state = self.__epsilon_close_map[self.__start]  # 当前处理的状态，初始化为初始状态的epsilon闭包
        # 状态
        all_states = [cur_state]  # 存所有状态，每出现一个状态就加入
        # 编号
        state = {frozenset(cur_state): 1, frozenset(): 0}  # 状态和编号的映射，把Φ记作0
        cur_state_index = 0  # 即将访问的temp的状态
        new_state_index = 2  # 下一个分配的编号
        end_set = set()  # 终止状态集
        while True:
            if cur_state_index >= len(all_states):
                # 没有新状态出现了，结束
                break
            cur_state = all_states[cur_state_index]
            if self.__end in cur_state:
                # 每访问一个新状态就更新一个终止状态集
                end_set.add(state[frozenset(cur_state)])
            record = []  # dfa的状态转换表的每一行
            for char in self.__char_set:  # 遍历每一个字母
                state_change = set()
                for i in cur_state:  # 遍历状态的每一个结点
                    for index in range(self.__size):  # 遍历结点的每一条边
                        if self.__graph[i][index] == char:  # 是当前字母，就把epsilon闭包并入
                            state_change = state_change | set(self.__epsilon_close_map[index])
                if frozenset(state_change) not in state:
                    # 这个新的状态没有出现过
                    state[frozenset(state_change)] = new_state_index
                    all_states.append(state_change)
                    new_state_index += 1
                if len(record) == 0:
                    record.append(state[frozenset(cur_state)])
                record.append(state[frozenset(state_change)])
                # 加入dfa边
                dfa.append([state[frozenset(cur_state)], char, state[frozenset(state_change)]])
            state_transition_table.append(record)
            cur_state_index += 1
        # 之前把空Φ也当成一个状态了，所以错了
        previous_no = {0: 0}  # 重新编号，上一次的编号，把Φ记作0
        for record in state_transition_table:
            # 第一次编号根据是否是终止状态比编号
            if record[0] in end_set:
                previous_no[record[0]] = 2  # 是终止态的标为2
            else:
                previous_no[record[0]] = 1  # 不是终止态的标为1
        while True:
            current_no = {0: 0}  # 重新编号，这一次的编号，dfa的编号和简化dfa编号的映射
            exist_states = dict()  # 这一次编号中已经出现的所有状态
            index_a = 1  # 分配状态编号
            for record in state_transition_table:
                # 给状态转换表的每一条记录重新编号
                record_state = ""
                for i in range(len(record)):
                    record_state += str(previous_no[record[i]])  # 拼接成字符串
                if record_state not in exist_states:  # 出现新状态
                    current_no[record[0]] = index_a
                    exist_states[record_state] = index_a
                    index_a += 1
                else:
                    current_no[record[0]] = exist_states[record_state]
            f = False
            for i in previous_no:
                if previous_no[i] != current_no[i]:  # 对比这一次的编号和上一次的编号
                    f = True
                    break
            if not f:  # 一致，结束
                break
            previous_no = current_no  # 不一致，继续
        final_dfa = []  # 最简dfa的边集
        visited1 = []  # 已经记录了nfa结点,record
        new_state_transition_table = [[]]
        for record in state_transition_table:
            if current_no[record[0]] in visited1:  # 记录过直接跳过
                continue
            new_record = [current_no[record[0]]]
            for i in range(1, len(record)):
                final_dfa.append([current_no[record[0]], self.__char_set[i - 1], current_no[record[i]]])
                new_record.append(current_no[record[i]])
            visited1.append(current_no[record[0]])
            new_state_transition_table.append(new_record)
        start_ = 1
        return current_no, start_, end_set, dfa, final_dfa, new_state_transition_table

    def draw_nfa(self):
        """
        nfa可视化
        :param start:  初始状态
        :param end:  终止状态
        :param edges:  边集
        """
        g = Digraph('G', filename='NFA.gv', format='png')
        g.attr(rankdir='LR')
        for i in range(len(self.__edges)):
            g.edge(str(self.__edges[i][0]), str(self.__edges[i][2]), label=str(self.__edges[i][1]))
        g.node(str(self.__end), shape='doublecircle')  # 结束节点双层
        g.node(str(self.__start), color='red')  # 开始节点红色
        g.view()

    def draw_dfa(self):
        """
        dfa可视化
        :param start: 起始状态
        :param end_set: 终止状态集
        :param dfa: dfa边集
        """
        if self.__current_no is None:
            self.__current_no, self.__start_, self.__end_set, self.__dfa, self.__final_dfa, self.__state_transition_table = self.__get_dfa()
        g = Digraph('G', filename='DFA.gv', format='png')
        g.attr(rankdir='LR')
        for i in range(len(self.__dfa)):
            g.edge(str(self.__dfa[i][0]), str(self.__dfa[i][2]), label=str(self.__dfa[i][1]))
        for i in self.__end_set:
            g.node(str(i), shape='doublecircle')  # 结束节点双层
        g.node(str(self.__start_), color='red')  # 开始节点红色
        g.view()

    def draw_and_simplify_dfa(self):
        """
        :param start: 起始状态
        :param end_set:  终止状态集
        :param final_dfa:  简化dfa的边集
        :param current_no: dfa编号与简化dfa编号之间的映射
        """
        if self.__current_no is None:
            self.__current_no, self.__start_, self.__end_set, self.__dfa, self.__final_dfa, self.__state_transition_table = self.__get_dfa()
        g = Digraph('G', filename='DFAs.gv', format='png')
        g.attr(rankdir='LR')
        for i in range(len(self.__final_dfa)):
            if self.__final_dfa[i][2] == 0:
                continue
            g.edge(str(self.__final_dfa[i][0]), str(self.__final_dfa[i][2]), label=str(self.__final_dfa[i][1]))
        for i in self.__end_set:
            g.node(str(self.__current_no[i]), shape='doublecircle')  # 结束节点双层
        g.node(str(self.__start_), color='red')  # 开始节点红色
        g.view()

    def match(self, str):
        """
        :param str: 要匹配的串
        :return:  布尔值，是否匹配
        """
        def match_str(str, index, cur):
            if index >= len(str):
                if cur in self.__end_set:
                    return True
                else:
                    return False
            for i in range(len(self.__char_set)):
                if self.__char_set[i] == str[index] and self.__state_transition_table[cur][i + 1] != 0:
                    return match_str(str, index + 1, self.__state_transition_table[cur][i + 1])
            return False

        if self.__current_no is None:
            self.__current_no, self.__start_, self.__end_set, self.__dfa, self.__final_dfa, self.__state_transition_table = self.__get_dfa()
        return match_str(str, 0, 1)
