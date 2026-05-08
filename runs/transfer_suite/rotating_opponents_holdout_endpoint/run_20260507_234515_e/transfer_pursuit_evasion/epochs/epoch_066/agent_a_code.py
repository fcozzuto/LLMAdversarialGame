def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles", []) or []
    oset = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    resources = observation.get("resources", []) or []
    rset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in oset:
                rset.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    bestv = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in oset:
                continue

            d_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if rset:
                d_res = min((nx - rx) * (nx - rx) + (ny - ry) * (ny - ry) for (rx, ry) in rset)
                res_bonus = 2000 if (nx, ny) in rset else 0
            else:
                d_res = 0
                res_bonus = 0

            v = (-d_op) * 3 + (-d_res) + res_bonus
            if best is None or v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)

    if best is None:
        for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in oset:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]