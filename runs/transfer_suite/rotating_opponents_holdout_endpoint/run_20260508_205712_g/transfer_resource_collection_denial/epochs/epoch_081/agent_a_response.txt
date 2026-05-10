def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if valid(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    if not res:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            cand = (d, nx, ny, dx, dy)
            if best is None or cand < best:
                best = cand
        return [int(best[3]), int(best[4])]

    # Greedy-race heuristic: maximize lead over opponent to the best next target.
    # Also prefer closer self distance when leads tie.
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    oxy = (ox, oy)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        selfp = (nx, ny)
        mind_s = None
        mind_o = None
        for r in res:
            d_s = abs(r[0] - nx) + abs(r[1] - ny)
            d_o = abs(r[0] - ox) + abs(r[1] - oy)
            if mind_s is None or d_s < mind_s:
                mind_s = d_s
            if mind_o is None or d_o < mind_o:
                mind_o = d_o
        # Count nearby resources to encourage staying on a good line.
        near = 0
        for r in res:
            if abs(r[0] - nx) + abs(r[1] - ny) <= 2:
                near += 1
        lead = mind_o - mind_s
        cand = (-lead, mind_s, -near, nx, ny, dx, dy)
        if best is None or cand < best:
            best = cand

    return [int(best[4]), int(best[5])]