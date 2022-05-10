def dfs_paths(graph, start, finish):
    paths = []
    visited = {k: False for k in graph.keys()}
    current_path = []
    _dfs_paths(graph, start, finish, visited, paths, current_path)
    return paths


def _dfs_paths(graph, start, finish, visited=None, paths=None, current_path=None):
    visited[start] = True
    current_path.append(start)

    if start == finish:
        paths.append(tuple(current_path))
    else:
        for v in graph[start].keys():
            if not visited[v]:
                _dfs_paths(graph, v, finish, visited, paths, current_path)

    current_path.pop(-1)
    visited[start] = False


def dfs_incremental_routes(graph):
    paths = []
    visited = {k: False for k in graph.flows.keys()}
    current_path = []
    _dfs_incremental_routes(graph, graph.start_vertex, visited, paths, current_path, '+')
    return paths


def _dfs_incremental_routes(graph, current_vertex, visited=None, paths=None, current_path=None, from_vertex=''):
    visited[current_vertex] = True
    current_path.append((current_vertex, from_vertex))

    if current_vertex == graph.target_vertex:
        paths.append(tuple(current_path))
    else:
        for j in graph[current_vertex].keys():
            if not visited[j]:
                f = graph[current_vertex][j]
                if f.max_value != f.value:
                    _dfs_incremental_routes(graph, j, visited, paths, current_path, f"+{current_vertex}")
        for v in graph.get_reversed()[current_vertex].keys():
            if not visited[v]:
                f = graph[v][current_vertex]
                if f.value > 0:
                    _dfs_incremental_routes(graph, v, visited, paths, current_path, f"-{current_vertex}")

    current_path.pop(-1)
    visited[current_vertex] = False


def dfs_mincut_search(graph):
    visited = {k: False for k in graph.flows.keys()}

    result = []
    queue = [(graph.start_vertex, '+')]

    while queue:
        current_vertex, mark = queue.pop(0)
        result.append((current_vertex, mark))
        visited[current_vertex] = True

        for j in graph[current_vertex].keys():
            if not visited[j]:
                f = graph[current_vertex][j]
                if f.max_value != f.value:
                    queue.append((j, f"+{current_vertex}"))
        for v in graph.get_reversed()[current_vertex].keys():
            if not visited[v]:
                f = graph[v][current_vertex]
                if f.value > 0:
                    queue.append((v, f"-{current_vertex}"))

    return result
