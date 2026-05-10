def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obs.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obs.add((int(p["x"]), int(p["y"])))

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # chebyshev (diagonals allowed)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
            else:
                x, y = int(r.get("x", -999)), int(r.get("y", -999))
        else:
            continue
        dS = dist(sx, sy, x, y)
        dO = dist(ox, oy, x, y)
        # Prefer resources we're closer to; also avoid those closer to opponent.
        # Secondary: smaller our distance.
        score = (dO - dS, -dS)
        res.append((score, x, y))
    if not res:
        return [0, 0]

    res.sort(key=lambda t: (t[0][0], t[0][1], -(t[1] + t[2])), reverse=True)
    _, tx, ty = res[0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]

    candidates = []
    for ddy in (-1, 0, 1):
        for ddx in (-1, 0, 1):
            if ddx == 0 and ddy == 0:
                continue
            cx, cy = sx + ddx, sy + ddy
            if not valid(cx, cy):
                continue
            d = dist(cx, cy, tx, ty)
            do = dist(cx, cy, ox, oy)
            candidates.append(((-d, do), ddx, ddy))
    if candidates:
        candidates.sort(key=lambda t: (t[0][0], t[0][1], t[1], t[2]), reverse=True)
        return [candidates[0][1], candidates[0][2]]
    return [0, 0]