def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    opp_next_opts = []
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if legal(nx, ny):
            opp_next_opts.append((nx, ny, dx, dy))
    if not opp_next_opts:
        opp_next_opts = [(ox, oy, 0, 0)]

    best = [0, 0]
    best_worst = None
    best_tieb = None

    for mydx, mydy in moves:
        nx, ny = sx + mydx, sy + mydy
        if not legal(nx, ny):
            continue
        worst = -1
        worst_tieb = None
        for ox2, oy2, odx, ody in opp_next_opts:
            dist = d2(nx, ny, ox2, oy2)
            if dist > worst:
                worst = dist
                worst_tieb = (odx, ody, ox2, oy2)
        tieb = (d2(nx, ny, ox, oy), d2(nx, ny, (w - 1) // 2, (h - 1) // 2))
        if best_worst is None or worst < best_worst or (worst == best_worst and tieb < best_tieb):
            best_worst = worst
            best_tieb = tieb
            best = [mydx, mydy]

    return best if best is not None else [0, 0]