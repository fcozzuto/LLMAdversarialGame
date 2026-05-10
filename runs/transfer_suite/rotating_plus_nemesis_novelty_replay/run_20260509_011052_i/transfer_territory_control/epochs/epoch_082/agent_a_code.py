def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = observation.get("resources", []) or []
    resources = []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        bestd = None
        for rx, ry in resources:
            dx = rx - sx
            dy = ry - sy
            d = dx * dx + dy * dy
            if bestd is None or d < bestd:
                bestd = d
                best = (rx, ry)
        tx, ty = best

    opp_dx = ox - sx
    opp_dy = oy - sy
    opp_dist = opp_dx * opp_dx + opp_dy * opp_dy

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                ndx = tx - nx
                ndy = ty - ny
                dtarget = ndx * ndx + ndy * ndy
                adx = ox - nx
                ady = oy - ny
                datk = adx * adx + ady * ady
                score = dtarget * 1000 - datk  # closer to target, farther from opponent
                candidates.append((score, dx, dy))
    candidates.sort(key=lambda t: (t[0], t[1], t[2]))

    for _, dx, dy in candidates:
        if dx != 0 or dy != 0:
            return [dx, dy]
    return [0, 0]