def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def to_set(lst):
        s = set()
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    self_set = to_set(observation.get("self_territory"))
    opp_set = to_set(observation.get("opponent_territory"))
    unclaimed_set = to_set(observation.get("unclaimed_cells"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    best = (-(10**18), 0)
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        if (nx, ny) in opp_set:
            gain = 30
        elif (nx, ny) in unclaimed_set:
            gain = 12
        elif (nx, ny) in self_set:
            gain = 6
        else:
            gain = 2

        d_opp = man(nx, ny, ox, oy)
        edge_bias = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_bias = 4

        score = gain * 5 - d_opp + edge_bias
        if score > best[0]:
            best = (score, i)

    return list(moves[best[1]]) if best[1] < len(moves) else [0, 0]