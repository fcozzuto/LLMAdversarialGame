def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def clamp01(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_val = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if resources:
            # Choose move that maximizes best "winning" resource advantage,
            # with tie-breaking toward nearest resource and some center bias.
            best_adv = -10**18
            best_d = 10**18
            for rx, ry in resources:
                myd = dist2(nx, ny, rx, ry)
                opd = dist2(ox, oy, rx, ry)
                adv = (opd - myd)  # positive means we are closer
                if adv > best_adv or (adv == best_adv and myd < best_d):
                    best_adv = adv
                    best_d = myd
            center_bias = -0.001 * dist2(nx, ny, cx, cy)
            val = best_adv + (-0.002 * best_d) + center_bias
        else:
            # No visible resources: push toward opponent while keeping center.
            toward_opp_x = clamp01(ox - nx)
            toward_opp_y = clamp01(oy - ny)
            opp_align = 1.0 if (dx == toward_opp_x and dy == toward_opp_y) else 0.0
            center_bias = -0.01 * dist2(nx, ny, cx, cy)
            val = 2.0 * opp_align + center_bias

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]