def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs.add((o[0], o[1]))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res.append((r[0], r[1]))
    if not res:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_adv = -10**9
    for rx, ry in res:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        if sd == 0:
            best = (rx, ry)
            best_adv = 10**9
            break
        if sd < od:
            adv = od - sd
            if adv > best_adv or (adv == best_adv and (rx + ry) < (best[0] + best[1])):
                best_adv = adv
                best = (rx, ry)

    if best is None:
        best = min(res, key=lambda p: (manh(sx, sy, p[0], p[1]), (p[0] + p[1])))

    rx, ry = best
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_sd = manh(sx, sy, rx, ry)
    cur_gap = manh(ox, oy, rx, ry) - cur_sd

    best_move = (0, 0)
    best_key = (-10**18, 10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        nsd = manh(nx, ny, rx, ry)
        nod = manh(ox, oy, rx, ry)
        gap = nod - nsd
        key = (gap, nsd)
        if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] < best_key[1]):
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]