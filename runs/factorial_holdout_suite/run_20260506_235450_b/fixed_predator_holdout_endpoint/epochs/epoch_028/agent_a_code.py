def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None  # (gain, -our_d, -rx, -ry, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        chosen = None  # (gain, -our_d, -rx, -ry)
        for rx, ry in resources:
            our_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            gain = opp_d - our_d  # positive means we are closer than opponent
            cand = (gain, -our_d, -rx, -ry)
            if chosen is None or cand > chosen:
                chosen = cand
        if chosen is None:
            continue
        key = (chosen[0], -(-chosen[1]), chosen[2], chosen[3], dx, dy)  # normalize for deterministic compare
        if best is None or key > best:
            best = key

    if best is None:
        return [0, 0]
    return [best[4], best[5]]