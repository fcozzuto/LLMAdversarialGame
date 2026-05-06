def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Choose target resource where we are most "ahead" vs opponent.
        best_adv = 10**18
        best_res_d = 10**18
        best_opp_d = 10**18
        tie_key = None

        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            if not (0 <= rx < w and 0 <= ry < h):
                continue
            ds = manh(nx, ny, rx, ry)
            do = manh(ox, oy, rx, ry)
            adv = ds - do  # lower means we are closer than opponent
            if (adv < best_adv) or (adv == best_adv and (ds, do, rx, ry) < (best_res_d, best_opp_d, rx, ry)):
                best_adv = adv
                best_res_d = ds
                best_opp_d = do
                tie_key = (rx, ry)

        if tie_key is None:
            continue

        # Value: strongly favor being ahead, then closeness to target, also slight preference to push away from opponent.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = - (abs(nx - cx) + abs(ny - cy))
        opp_pressure = manh(nx, ny, ox, oy)

        val = (-1000 * best_adv) - 3 * best_res_d + 0.2 * best_opp_d + 0.01 * center - 0.05 * opp_pressure
        if (val > best_val) or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]