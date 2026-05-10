def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def opp_next_est():
        if not resources:
            return ox, oy
        # anticipate row-sweep: prefer resource with same y close, else closest
        best = None
        bestk = None
        for rx, ry in resources:
            dy = abs(ry - oy)
            d = man(ox, oy, rx, ry)
            k = (dy, d, ry, rx)
            if bestk is None or k < bestk:
                bestk = k
                best = (rx, ry)
        rx, ry = best
        dx = 0 if rx == ox else (1 if rx > ox else -1)
        dy = 0 if ry == oy else (1 if ry > oy else -1)
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return nx, ny
        # fallback: keep if blocked
        return ox, oy

    enx, eny = opp_next_est()

    if not resources:
        # deterministic corner retreat/advance away from opponent
        return [1 if sx <= ox else -1 if sx > ox else 0, 1 if sy <= oy else -1 if sy > oy else 0]

    def cell_value(mx, my, ex, ey):
        best_adv = None
        best_d = None
        for rx, ry in resources:
            dm = man(mx, my, rx, ry)
            de = man(ex, ey, rx, ry)
            adv = de - dm  # positive means we can reach first vs estimated opponent
            # also bias toward "capturable" cells: closer to some resource
            d2 = dm
            k = (-adv, d2, abs(rx - mx), abs(ry - my))
            if best_adv is None or k < best_d:
                best_adv = adv
                best_d = k
        # translate back to comparable score: larger is better
        return best_adv if best_adv is not None else -10**9

    # choose move that maximizes our next-step advantage against estimated opponent position
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sc = cell_value(nx, ny, enx, eny)
        # tie-break deterministically: prefer staying on same x/y progress, then lower coords
        k = (-sc, abs(nx - sx) + abs(ny - sy), nx, ny)
        if best_score is None or k < best_score:
            best_score = k
            best_move = [dx, dy]

    return best_move