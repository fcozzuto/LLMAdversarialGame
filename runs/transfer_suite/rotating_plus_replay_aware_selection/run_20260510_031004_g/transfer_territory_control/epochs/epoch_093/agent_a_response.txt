def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    un_list = [tuple(c) for c in unclaimed if len(c) == 2 and inb(c[0], c[1]) and not blocked(c[0], c[1])]
    opp_list = [p for p in opp_terr if inb(p[0], p[1]) and not blocked(p[0], p[1])]

    def nearest_dist(x, y, points):
        best = 10**9
        for px, py in points[:8]:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best if best != 10**9 else None

    target_un = un_list if un_list else []
    target_opp = opp_list if opp_list else []

    def score_pos(x, y):
        if not inb(x, y) or blocked(x, y):
            return -10**9
        s = 0
        t_un = (x, y) in unclaimed
        if t_un:
            s += 22
        if (x, y) in opp_terr:
            s += 32
        if (x, y) in self_terr:
            s += 2
        adj_un = 0
        adj_self = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            if (nx, ny) in unclaimed:
                adj_un += 1
            if (nx, ny) in self_terr:
                adj_self += 1
        s += adj_un * 7 + adj_self * 3
        if target_un:
            d = nearest_dist(x, y, target_un)
            if d is not None:
                s += max(0, 10 - d)
        elif target_opp:
            d = nearest_dist(x, y, target_opp)
            if d is not None:
                s += max(0, 6 - d) * 2
        return s

    # Ensure unclaimed is a set for adjacency checks without heavy work
    un_set = set(map(tuple, unclaimed or []))
    if un_set:
        pass

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if score_pos(nx, ny) > best_score:
            best_score = score_pos(nx, ny)
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]