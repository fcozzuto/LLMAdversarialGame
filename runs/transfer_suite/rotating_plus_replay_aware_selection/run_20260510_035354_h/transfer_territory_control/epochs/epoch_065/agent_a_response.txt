def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    opp_terr_list = observation.get("opponent_territory") or []
    self_terr_list = observation.get("self_territory") or []
    unclaimed_list = observation.get("unclaimed_cells") or []

    oset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    opset = {(p[0], p[1]) for p in opp_terr_list if isinstance(p, (list, tuple)) and len(p) >= 2}
    uset = {(p[0], p[1]) for p in self_terr_list if isinstance(p, (list, tuple)) and len(p) >= 2}
    usn = {(p[0], p[1]) for p in unclaimed_list if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    ox, oy = observation.get("opponent_position", (0, 0))
    targets = list(usn) if usn else list(opset) if opset else [(ox, oy)]
    if not targets:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in oset:
            continue

        if (nx, ny) in opset:
            gain = 2.4
        elif (nx, ny) in usn:
            gain = 1.9
        elif (nx, ny) in uset:
            gain = 0.6
        else:
            gain = 1.1

        d_t = 10**9
        tx_best, ty_best = None, None
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            if d < d_t:
                d_t = d
                tx_best, ty_best = tx, ty

        d_opp = man(nx, ny, ox, oy)
        opp_penalty = 0.12 * (7 - d_opp) if d_opp < 7 else 0.0

        # Slight preference to line up with the chosen target deterministically
        align = 0.0
        if tx_best is not None:
            align = 0.08 * (1 if (tx_best - nx == 0 or ty_best - ny == 0 or abs(tx_best - nx) == abs(ty_best - ny)) else 0)

        score = gain - 0.08 * d_t - opp_penalty + align
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]