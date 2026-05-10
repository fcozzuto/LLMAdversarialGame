def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, dict):
            x, y = p.get("x"), p.get("y")
        else:
            x, y = (p[0], p[1]) if p and len(p) >= 2 else (None, None)
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, dict):
            x, y = p.get("x"), p.get("y")
        else:
            x, y = (p[0], p[1]) if p and len(p) >= 2 else (None, None)
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    if res:
        tx, ty = min(res, key=lambda t: (t[0] - sx) ** 2 + (t[1] - sy) ** 2)
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        dtx = (nx - tx) ** 2 + (ny - ty) ** 2
        dop = (nx - ox) ** 2 + (ny - oy) ** 2
        penalty = 0
        if dop == 0:
            penalty += 10 ** 9
        if dop <= 2:
            penalty += 1000
        score = penalty + dtx - 0.01 * dop
        cand = (score, dx, dy)
        if best is None or cand < best:
            best = cand

    return [best[1], best[2]] if best else [0, 0]