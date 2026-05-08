def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        w, h = int(w), int(h)
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        return [0, 0]

    blocked = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    res = observation.get("resources") or []
    targets = []
    for r in res:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                targets.append((x, y))
        except:
            pass

    if targets:
        tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        tx, ty = ox, oy

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        adv = - (abs(tx - nx) + abs(ty - ny) == 0)
        key = (d, adv, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    if best is not None:
        return best
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            return [dx, dy]
    return [0, 0]