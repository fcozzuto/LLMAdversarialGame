def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def dist_to_center(x, y):
        return abs(x - cx) + abs(y - cy)

    def adj_has_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp_set:
                        return True
        return False

    best = None
    bestv = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        val = 0.0
        ndc = dist_to_center(nx, ny)
        val += -0.35 * ndc
        if (nx, ny) in opp_set:
            val += 6.0 + 0.1 * (observation.get("turn_index", 0) % 2)
        elif (nx, ny) in unclaimed:
            val += 2.0
            if adj_has_opp(nx, ny):
                val += 1.5
        if (nx, ny) in self_set:
            val += 0.3
        # Prefer tightening against opponent direction even without direct capture
        oppx, oppy = observation["opponent_position"]
        val += -0.08 * d((nx, ny), (oppx, oppy))
        if adj_has_opp(nx, ny) and (nx, ny) not in opp_set:
            val += 0.7
        if val > bestv:
            bestv = val
            best = [dx, dy]
    return best