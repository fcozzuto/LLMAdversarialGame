def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            try:
                obs.add((int(p[0]), int(p[1])))
            except:
                pass

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
                res.append((x, y))
            except:
                pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if w and h:
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
        if (nx, ny) in obs:
            continue

        if res:
            tx, ty = min(res, key=lambda t: (t[0] - nx) * (t[0] - nx) + (t[1] - ny) * (t[1] - ny))
            score = -((tx - nx) * (tx - nx) + (ty - ny) * (ty - ny))
        else:
            score = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)  # flee when no resources known

        # deterministic tie-break: prefer smaller dx, then dy, then higher score
        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]

    cand.sort(key=lambda t: (-(t[0]), t[1], t[2]))
    _, dx, dy = cand[0]
    return [int(dx), int(dy)]