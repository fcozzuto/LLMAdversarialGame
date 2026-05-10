def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, dict):
            q = p.get("position") or (p.get("x"), p.get("y"))
            if q and len(q) >= 2:
                obs.add((int(q[0]), int(q[1])))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict):
            q = r.get("position") or (r.get("x"), r.get("y"))
            if q and len(q) >= 2:
                res.append((int(q[0]), int(q[1])))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18

    def md(a, b, c, d):
        x = a - c
        y = b - d
        return abs(x) + abs(y)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        if res:
            dmin = min(md(nx, ny, rx, ry) for rx, ry in res)
            rscore = -dmin
        else:
            rscore = 0

        dop = md(nx, ny, ox, oy)
        oscore = dop if dop <= 4 else dop // 2

        v = rscore * 5 + oscore * 3
        if (best is None) or (v > bestv) or (v == bestv and (dx, dy) < best):
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]