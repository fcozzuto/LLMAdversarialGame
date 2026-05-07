def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def neighbors(x, y):
        opts = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    opts.append((nx, ny, dx, dy))
        return opts

    best_res = None
    best_val = None
    for rx, ry in resources:
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        gap = opp_d - self_d
        opp_urgency = 20 // (opp_d + 1)  # smaller opp_d => larger urgency
        val = gap * 2 + opp_urgency
        # tie-break: prefer closer to us, then lexicographically
        key = (val, -self_d, -rx, -ry)
        if best_val is None or key > best_val:
            best_val = key
            best_res = (rx, ry)

    tx, ty = best_res
    cand = neighbors(sx, sy)
    # Choose move that most reduces our distance to the chosen target; secondary: increases opp distance
    best_move = (0, 0, 10**9, -10**9)
    for nx, ny, dx, dy in cand:
        d1 = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # compare after our move: opponent could still be closer, so also encourage increasing their effective distance
        opp_after = man(ox, oy, tx, ty)
        score = (-d1, opp_after - opp_d)  # opp_after-oppsame = 0; keep deterministic tie-break via lex below
        if (d1, -dx, -dy) < (best_move[2], best_move[0]*-1, best_move[1]*-1):
            best_move = (dx, dy, d1, opp_after)
    return [int(best_move[0]), int(best_move[1])]