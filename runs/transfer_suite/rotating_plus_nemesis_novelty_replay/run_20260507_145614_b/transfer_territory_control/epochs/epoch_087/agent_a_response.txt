def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))
    opp_s = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opp_s.add((x, y))
    self_s = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                self_s.add((x, y))

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    def edge_bias(x, y):
        return (1 if x == 0 or x == w - 1 else 0) + (1 if y == 0 or y == h - 1 else 0)

    def eval_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        val = 0
        if (x, y) in unclaimed:
            val += 8
        if (x, y) in self_s:
            val += 2
        if (x, y) in opp_s:
            val -= 18
        e = edge_bias(x, y)
        val += 3 * e
        adj_our = 0
        adj_opp = 0
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in self_s:
                adj_our += 1
            elif (nx, ny) in opp_s:
                adj_opp += 1
        val += 1.2 * adj_our
        if (x, y) in opp_s:
            val += 2.5 * adj_our
            val += 0.8 * adj_opp
        else:
            val += 0.2 * adj_opp
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(x - cx) + abs(y - cy)
        val += 0.01 * dist_center
        return val

    moves = [[0, 0], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        v = eval_cell(nx, ny)
        if v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best