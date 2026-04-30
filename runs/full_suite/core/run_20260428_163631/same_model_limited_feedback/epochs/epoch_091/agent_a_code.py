def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # fallback: move toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = clamp(tx - sx, -1, 1)
        dy = clamp(ty - sy, -1, 1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    opp = (ox, oy)
    best = None  # (advantage, self_dist, x, y)
    for r in resources:
        sr = (r[0], r[1])
        sd = dist((sx, sy), sr)
        od = dist(opp, sr)
        adv = od - sd
        key = (adv, sd, r[0], r[1])
        if best is None or key > best:
            best = key

    target = (best[2], best[3])
    tx, ty = target

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    deltas.sort(key=lambda d: (d[0]!=clamp(tx-sx,-1,1) or d[1]!=clamp(ty-sy,-1,1), d[0], d[1]))

    best_move = None  # (score, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        self_d = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(nx - ox) + abs(ny - oy)
        score = (-self_d, opp_d, dx, dy)
        if best_move is None or score > best_move:
            best_move = score

    if best_move is None:
        return [0, 0]
    return [best_move[2], best_move[3]]