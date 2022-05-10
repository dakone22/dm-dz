from random import choice

import plantuml
from graph import walk


class Solver:
    def __init__(self, graph):
        self.graph = graph
        self.out = plantuml.Output()
        self.flow = 0

    def run(self):
        self.stage1()
        self.stage2()
        # print(self.out.markdown_text)

    def stage1(self):
        self.out.text(r"1. $\varphi = 0$")
        self.out.text(r"2. $\varphi_п - ?$")
        
        _step = 0
        for path in self.graph.paths:
            delta = []
            for from_vertex, to_vertex in walk(path):
                f = self.graph.get_flow(from_vertex, to_vertex)
                delta.append((f.max_value, f.value))
        
            min_delta = min([m - v for m, v in delta])
            if min_delta > 0:
                _step += 1; __path = ','.join([f'x_{{{p}}}' for p in path])
                __delta = ','.join([f'{m}-{v}' for m, v in delta])
        
                _sat = []
                for from_vertex, to_vertex in walk(path):
                    self.graph.increment_flow(from_vertex, to_vertex, min_delta)
                    _sat.append((from_vertex, to_vertex))
                self.flow += min_delta
        
                __sat = ','.join([f"(x_{{{s}}}, x_{{{e}}})" for s, e in _sat if self.graph.is_saturated_flow(s, e)])
                self.out.text(fr"    {_step}. $({__path})$", end='\n'*2)
                self.out.text(fr"       $\delta^* = min\{{{__delta}\}} = {min_delta}$", end='\n'*2)
                self.out.text( r"       $\Rightarrow \text{ребра } " + __sat + r"\text{ - насыщенные}$", end='\n'*2)
                self.out.text(fr"       $\varphi = {self.flow}$")
                self.out.text(  "       ", end=''); self.out.image(self.graph.current_state_image())
        
        self.out.text("       ---\n"*2)
        self.out.text(r"       $\varphi_п =" + f"{self.flow}$")
        self.out.image(self.graph.current_state_image())
        self.out.text("       ---\n"*2)
        
    def stage2(self):
        self.out.text(fr"3. $\varphi_{{\max}}$ -- ?", end='\n'*2)

        _step = 0
        while True:
            incremental_routes = self.graph.get_incremental_routes()
            if not incremental_routes:
                break
        
            incremental_route = choice(incremental_routes)
            edges = [(int(s[1:]), end, s[0]) for end, s in incremental_route[1:]]
        
            delta, phi = [], []
            for from_vertex, to_vertex, direction in edges:
                if direction == '+':
                    f = self.graph.get_flow(from_vertex, to_vertex)
                    delta.append((f.max_value, f.value))
                else:
                    f = self.graph.get_flow(to_vertex, from_vertex)
                    phi.append(f.value)
        
            if delta and phi:
                __delta = ','.join([f'{m}-{v}' for m, v in delta]); __phi = ','.join([f'{v}' for v in phi])
        
                delta = [m - v for m, v in delta]
                eps = min([min(delta), min(phi)])
        
                if eps > 0:
                    _step += 1; __path = ','.join([f'x_{{{p}}}({x})' for p, x in incremental_route])
                    __forward_edges = ','.join([f"(x_{{{from_vertex}}},x_{{{to_vertex}}})" for from_vertex, to_vertex, direction in edges if direction == '+'])
                    __backward_edges = ','.join([f"(x_{{{from_vertex}}},x_{{{to_vertex}}})" for from_vertex, to_vertex, direction in edges if direction == '-'])
        
                    for from_vertex, to_vertex, direction in edges:
                        if direction == '+':
                            self.graph.increment_flow(from_vertex, to_vertex, eps)
                        else:
                            self.graph.increment_flow(to_vertex, from_vertex, -eps)
                    self.flow += eps
        
                    self.out.text(f"    {_step}. Удалось пометить: $({__path})$", end='\n'*2)
                    self.out.text(fr"       Прямые рёбра: ${__forward_edges}$", end='\n'*2)
                    self.out.text(fr"       Обратные рёбра: ${__backward_edges}$", end='\n'*2)
                    self.out.text(fr"       $\delta^* = min\{{{__delta}\}} = {min(delta)}$", end='\n'*2)
                    self.out.text(fr"       $\varphi^* = min\{{{__phi}\}} = {min(phi)}$", end='\n'*2)
                    self.out.text(fr"       $\varepsilon^* = min\{{{min(delta)}, {min(phi)}\}} = {eps}$", end='\n'*2)
                    self.out.text(fr"       $\varphi={self.flow}$", end='\n'*2)
                    self.out.text("       ", end=''); self.out.image(self.graph.current_state_image(dict(incremental_route)))

        self.out.text("---")

        if _step == 0:
            self.out.text("# Похоже, не нашлось увеличивающих маршрутов. Попробуйте перезапустить, чтобы найти другое случайное решение")
            return

        mincut, mincut_flow = self.graph.get_mincut()
        if mincut_flow != self.flow:
            self.out.text("# Похоже, пропускная способность минимального разреза не ровна максимальному потоку. Если это случается, значит что-то явно пошло не так.")
            return

        self.out.text(f"## Минимальный разрез (выделенные вершины):")
        self.out.image(self.graph.current_state_image(dict(mincut)))

        self.out.text("---")
        self.out.text(f"Достигнут полный поток за {_step+1} итераций.")
        self.out.text(f"Нашли {_step} увеличивающих маршрутов.")
        self.out.text(f"...")
        self.out.text(f"Подтверждается теорема Форда-Фалкерсона ...")
        self.out.text("\n" + fr"$\varphi_{{max}} = {self.flow}$")


if __name__ == "__main__":
    # fast debug
    from graph import Graph


    def get_graph():
        """Define your graph here"""
        vertex_number = 10

        start_vertex, target_vertex = 0, vertex_number - 1
        graph_dict = {i: {} for i in range(vertex_number)}

        # graph[from_vertex_i] = {to_vertex_j: max_flow_j, ...}
        graph_dict[0] = {1: 3, 2: 17, 3: 4}
        graph_dict[1] = {4: 2, 7: 5, 8: 3}
        graph_dict[2] = {4: 9}
        graph_dict[3] = {2: 3, 5: 7, 8: 12}
        graph_dict[4] = {7: 4, 6: 2}
        graph_dict[5] = {2: 5, 9: 5}
        graph_dict[6] = {5: 6, 9: 5}
        graph_dict[7] = {9: 12}
        graph_dict[8] = {9: 8}
        graph_dict[9] = {}

        return Graph(graph_dict, start_vertex, target_vertex)

    solver = Solver(get_graph())
    solver.run()
    print(solver.out.markdown_text)
