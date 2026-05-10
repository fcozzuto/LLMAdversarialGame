def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_move = [0, 0]

    def opp_next_dist(rx, ry):
        # opponent chooses a move that minimizes its distance to (rx, ry), tie-break by staying (0,0) then lex.
        bd = None
        bt = (0, 0)
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                nx, ny = ox, oy
            d = man(nx, ny, rx, ry)
            if bd is None or d < bd or (d == bd and (dx, dy) < bt):
                bd = d
                bt = (dx, dy)
        return bd

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        worst_adv = None
        worst_t = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = opp_next_dist(rx, ry)
            adv = od - sd  # higher => we are closer after opponent's reply
            if worst_adv is None or adv < worst_adv or (adv == worst_adv and sd < worst_t):
                worst_adv = adv
                worst_t = sd
        key = (worst_adv, -worst_t, nx, ny, dx, dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return best_move