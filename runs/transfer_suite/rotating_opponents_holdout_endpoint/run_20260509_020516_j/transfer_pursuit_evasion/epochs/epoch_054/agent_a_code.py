def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    resources = observation.get("resources") or []
    pts = []
    for r in resources:
        try:
            if isinstance(r, dict):
                x, y = r.get("x"), r.get("y")
            else:
                x, y = r[0], r[1]
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                pts.append((x, y))
        except Exception:
            pass

    target = (ox, oy)
    if pts:
        best = None
        bd = None
        for x, y in pts:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if bd is None or d < bd:
                bd = d
                best = (x, y)
        if best is not None:
            target = best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    tx, ty = target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        score = -d
        if dx == 0 and dy == 0:
            score -= 0.05
        score -= 0.001 * (abs(nx - ox) + abs(ny - oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]