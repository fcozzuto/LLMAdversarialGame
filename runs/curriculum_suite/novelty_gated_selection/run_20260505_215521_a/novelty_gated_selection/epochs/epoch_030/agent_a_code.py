def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])

    resources = observation.get("resources", None) or []
    obst_raw = observation.get("obstacles", None) or []

    obst = set()
    for p in obst_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.add((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obst)

    def best_res_dist(x, y):
        if not res:
            return abs(x - w // 2) + abs(y - h // 2)
        return min(abs(x - rx) + abs(y - ry) for rx, ry in res)

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        rsd = best_res_dist(nx, ny)
        ods = abs(nx - ox) + abs(ny - oy)
        on_res = 1 if (nx, ny) in res else 0
        score = -rsd + 0.15 * ods + 5 * on_res
        cand.append((score, nx, ny, dx, dy))

    if not cand:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    cand.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
    return [cand[0][3], cand[0][4]]