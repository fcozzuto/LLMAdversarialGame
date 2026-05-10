def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_cells = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_cells.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    if not unclaimed:
        target = (ox, oy)
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

        def md(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        best_t = None
        best_s = -10**18
        for t in unclaimed:
            sd = md((sx, sy), t)
            od = md((ox, oy), t)
            s = (od - sd) - 0.12 * (abs(t[0] - cx) + abs(t[1] - cy))
            if s > best_s:
                best_s = s
                best_t = t
        target = best_t if best_t is not None else (ox, oy)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs_cells:
            continue
        val = - (abs(nx - target[0]) + abs(ny - target[1]))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]