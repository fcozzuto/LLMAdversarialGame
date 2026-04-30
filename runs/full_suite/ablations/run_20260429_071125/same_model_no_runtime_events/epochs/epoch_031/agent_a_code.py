def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        cx, cy = w // 2, h // 2
        dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best_m = (0, 0)
        best_s = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                s = -(abs(nx - cx) + abs(ny - cy)) + 0.2 * (abs(nx - ox) + abs(ny - oy))
                if s > best_s:
                    best_s = s
                    best_m = (dx, dy)
        return [int(best_m[0]), int(best_m[1])]
    closest = None
    best_d = 10**18
    for x, y in res:
        d = abs(x - sx) + abs(y - sy)
        if d < best_d:
            best_d = d
            closest = (x, y)
    tx, ty = closest
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            d_self = abs(nx - tx) + abs(ny - ty)
            d_opp = abs(nx - ox) + abs(ny - oy)
            s = -d_self + 0.15 * d_opp
            if s > best_s:
                best_s = s
                best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]