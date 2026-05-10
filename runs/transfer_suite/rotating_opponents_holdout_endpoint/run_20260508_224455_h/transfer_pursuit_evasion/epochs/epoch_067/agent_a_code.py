def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, dict):
            x, y = int(p.get("x", -1)), int(p.get("y", -1))
        else:
            x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, dict):
            x, y = int(r.get("x", -1)), int(r.get("y", -1))
        else:
            x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    role = str(observation.get("self_role") or observation.get("role") or "").lower()
    evader = ("evader" in role) or ("escape" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        if res:
            d0 = abs(nx - sx) + abs(ny - sy)
            dr = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
            v = -dr * 10 - d0
        else:
            dist = max(abs(nx - ox), abs(ny - oy))
            v = dist if evader else -dist
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]