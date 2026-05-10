def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles if p is not None and len(p) >= 2)

    resources = observation.get("resources") or []
    res = [(int(r[0]), int(r[1])) for r in resources if r is not None and len(r) >= 2]
    if not res:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    nx_target, ny_target = None, None
    bestd = 10**9
    for rx, ry in res:
        if (rx, ry) in obs:
            continue
        d = man(sx, sy, rx, ry)
        if d < bestd:
            bestd = d
            nx_target, ny_target = rx, ry

    if nx_target is None:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18
    opp_best = -1

    for dx, dy in dirs:
        tx, ty = sx + dx, sy + dy
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
            continue

        d_to_res = man(tx, ty, nx_target, ny_target)
        d_to_opp = man(tx, ty, ox, oy)

        take = 1 if (tx, ty) in set(res) else 0
        val = take * 10**6 - d_to_res + (d_to_opp - man(sx, sy, ox, oy))
        if val > best_val or (val == best_val and (d_to_opp > opp_best or (d_to_opp == opp_best and (dx, dy) < best))):
            best_val = val
            opp_best = d_to_opp
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]