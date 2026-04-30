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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_sc = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        center_bias = - (abs(rx - cx) + abs(ry - cy)) * 0.001
        sc = (od - sd) - sd * 0.01 + center_bias
        if best_sc is None or sc > best_sc or (sc == best_sc and sd < md(sx, sy, best[0], best[1])):
            best_sc = sc
            best = (rx, ry)

    tx, ty = best
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best_move = None
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = md(nx, ny, tx, ty)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) == (0, 0)):
            best_d = d
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move