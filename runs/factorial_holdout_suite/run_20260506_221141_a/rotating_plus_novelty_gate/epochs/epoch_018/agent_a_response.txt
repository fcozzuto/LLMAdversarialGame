def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                res.append((x, y))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def best_adv(px, py):
        best = -10**9
        for tx, ty in res:
            sd = abs(tx - px) + abs(ty - py)
            od = abs(tx - ox) + abs(ty - oy)
            v = od - sd
            if v > best:
                best = v
        return best

    moves = []
    # deterministic order: prefer diagonals, then cardinal, then stay (but always via sorted tuples)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if not (dx == 0 and dy == 0):
                moves.append((dx, dy))
    moves.append((0, 0))

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        adv = best_adv(nx, ny)
        nearest_sd = min(abs(tx - nx) + abs(ty - ny) for tx, ty in res)
        opp_nearest_sd = min(abs(tx - ox) + abs(ty - oy) for tx, ty in res)
        key = (adv, -nearest_sd, opp_nearest_sd, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]