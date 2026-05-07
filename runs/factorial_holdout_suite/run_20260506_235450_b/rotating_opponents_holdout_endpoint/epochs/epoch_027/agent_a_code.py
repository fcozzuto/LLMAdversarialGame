def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            obs_set.add((int(a["x"]), int(a["y"])))
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            obs_set.add((int(a[0]), int(a[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_adv_from(px, py):
        best = None
        for rx, ry in resources:
            myd = dist(px, py, rx, ry)
            opd = dist(ox, oy, rx, ry)
            adv = myd - opd
            key = (adv, myd, rx, ry)
            if best is None or key < best:
                best = key
        return best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        candidates = [(0, 0, sx, sy)]

    best_move = None
    for dx, dy, nx, ny in candidates:
        key = best_adv_from(nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)
    return [int(best_move[1]), int(best_move[2])]