def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("run" in role) or ("away" in role) or ("escape" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    cur_d2 = dist2(sx, sy, ox, oy)

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d2 = dist2(nx, ny, ox, oy)
        # secondary features: avoid being boxed in by obstacles
        free_n = 0
        for adx, ady in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
            tx, ty = nx + adx, ny + ady
            if in_bounds(tx, ty):
                free_n += 1

        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.0001

        if is_evader:
            # maximize distance, prefer moves that increase it and keep escape freedom
            score = d2 + (0.5 if d2 > cur_d2 else 0.0) + free_n * 0.01 + center_bias
        else:
            # minimize distance, prefer capturing lines by keeping opponent distance low and not getting stuck
            score = -d2 + (0.5 if d2 < cur_d2 else 0.0) + free_n * 0.005 + center_bias

        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return best