def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        # diagonal-allowed shortest in Chebyshev metric
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Prefer moves that improve lead on best attainable resource (lookahead 1 turn)
    best_mv = [0, 0]
    best_sc = None
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        best_lead = None
        best_self_d = None
        for rx, ry in resources:
            sd = dist((nx, ny), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            lead = od - sd
            # tie-break: closer self distance, and prefer resources farther from our start corner (less dithering)
            key = (lead, -sd, -(abs(rx - (w - 1)) + abs(ry - (h - 1))))
            if best_lead is None or key > (best_lead, -best_self_d, 0):
                best_lead = lead
                best_self_d = sd

        # score: maximize lead; if equal, minimize self distance; slight preference for moving away from obstacles is implicit
        sc = (best_lead, -best_self_d, -abs(nx - ox) - abs(ny - oy))
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = [dx, dy]

    return best_mv