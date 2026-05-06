def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obst)

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources:
        return [0, 0]

    # Anti-sweep response:
    # Prefer resources that are hard for opponent to reach quickly and also not on opponent's current sweep line.
    opp_row = oy
    opp_col = ox
    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)

        # If on opponent row/col, treat as likely swept; penalize.
        line_pen = 0
        if ry == opp_row:
            line_pen += 3
        if rx == opp_col:
            line_pen += 2

        # If we are closer, great; otherwise choose only if opponent is much worse.
        # Favor tighter races using a non-linear gap.
        gap = (do - ds)
        score = (gap * 4) - line_pen - ds * 0.15 + (10 if gap >= 2 else 0)
        # Slight tie-break: pick more central-ish to reduce getting stuck on corners/edges.
        score -= abs(rx - (w - 1) / 2) * 0.01 + abs(ry - (h - 1) / 2) * 0.01

        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # Greedy toward target with a deterministic obstacle-aware bias.
        curd = abs(sx - tx) + abs(sy - ty)
        nd = abs(nx - tx) + abs(ny - ty)
        prog = (curd - nd)
        # Avoid stepping onto opponent if adjacent/diagonal (likely contested).
        opp_adj = 1 if (abs(nx - ox) <= 1 and abs(ny - oy) <= 1) else 0
        val = prog * 10 - nd * 0.1 - opp_adj * 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]