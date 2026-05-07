def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (sx, sy))
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
        except Exception:
            x, y = p.get("x"), p.get("y")
        obstacles.add((int(x), int(y)))

    resources = observation.get("resources", []) or []
    rpos = []
    for r in resources:
        if isinstance(r, dict):
            if "position" in r:
                x, y = r["position"]
            else:
                x, y = r.get("x"), r.get("y")
        else:
            x, y = r
        if x is None or y is None:
            continue
        rpos.append((int(x), int(y)))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not rpos:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_adv = None
        for rx, ry in rpos:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = myd - opd  # smaller => more likely to beat opponent
            if best_adv is None or adv < best_adv:
                best_adv = adv
        key = (best_adv, abs(dx), abs(dy), dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]