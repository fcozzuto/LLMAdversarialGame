def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    sp = observation.get("self_position") or (0, 0)
    if isinstance(sp, dict):
        sp = sp.get("position") or sp.get("pos") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    op = observation.get("opponent_position") or (sx, sy)
    if isinstance(op, dict):
        op = op.get("position") or op.get("pos") or (sx, sy)
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for o in observation.get("obstacles") or []:
        x, y = o, None
        if isinstance(o, dict):
            p = o.get("position") or o.get("pos")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
        elif isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = o[0], o[1]
        if y is not None:
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        p = r
        if isinstance(r, dict):
            p = r.get("position") or r.get("pos")
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        target = (tx, ty)
    else:
        target = (ox, oy)

    best = None
    bestd = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = abs(nx - target[0]) + abs(ny - target[1])
        if d < bestd or (d == bestd and (dx, dy) < best):
            bestd = d
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]