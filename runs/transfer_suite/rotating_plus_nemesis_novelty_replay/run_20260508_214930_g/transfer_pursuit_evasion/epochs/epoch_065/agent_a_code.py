def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res_list.append((x, y))

    candidates = []
    for dx, dy in deltas:
        if not legal(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        if res_list:
            nearest = min(manh(nx, ny, rx, ry) for rx, ry in res_list)
            target = min(res_list, key=lambda p: (manh(nx, ny, p[0], p[1]), p[0], p[1]))
            tx, ty = target
            score = -nearest * 10 + (w*h - manh(nx, ny, ox, oy)) + (100 - manh(nx, ny, tx, ty))
        else:
            score = (w*h - manh(nx, ny, ox, oy)) - manh(nx, ny, (w//2), (h//2)) * 0
        candidates.append((score, nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[3], t[4]))
    best = candidates[0]
    return [int(best[3]), int(best[4])]