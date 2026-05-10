def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "")).lower()
    evader = ("evader" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    resources = observation.get("resources", []) or []
    if resources:
        best_r = None
        best_d = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if (rx, ry) in blocked:
                    continue
                d = manhattan(sx, sy, rx, ry)
                if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_r):
                    best_d = d
                    best_r = (rx, ry)
        target = best_r if best_r is not None else (ox, oy)
    else:
        target = (ox, oy)

    if evader:
        tx, ty = (0, 0)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = corners[0]
        bestv = -1
        for cx, cy in corners:
            v = manhattan(cx, cy, ox, oy)
            if v > bestv or (v == bestv and (cx, cy) > best):
                bestv = v
                best = (cx, cy)
        tx, ty = best
    else:
        tx, ty = target

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = cand[4]
    best_val = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        d = manhattan(nx, ny, tx, ty)
        oppd = manhattan(nx, ny, ox, oy)
        val = (-d, oppd) if not evader else (d, -oppd)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]