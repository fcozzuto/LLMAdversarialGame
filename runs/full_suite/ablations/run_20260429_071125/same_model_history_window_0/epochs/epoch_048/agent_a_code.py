def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def clamp(v):
        return -1 if v < -1 else (1 if v > 1 else v)

    def best_resource():
        best = None
        best_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            val = (od - sd) * 1000 - sd  # capture advantage, then closer
            if val > best_val:
                best_val = val
                best = (rx, ry)
        return best

    target = best_resource()
    if target is None:
        return [0, 0]
    tx, ty = target

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                continue
            nx, ny = sx + mx, sy + my
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            nd = abs(tx - nx) + abs(ty - ny)
            od = abs(tx - ox) + abs(ty - oy)
            me_adv = (od - nd)
            score = me_adv * 1000 - nd
            candidates.append((score, mx, my))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [dx, dy]