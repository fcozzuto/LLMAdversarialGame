def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {tuple(p) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    us = (sx, sy)
    op = (ox, oy)

    def best_target():
        res = [tuple(r) for r in resources]
        if not res:
            return None
        best = None
        for r in res:
            ds = md(us, r)
            do = md(op, r)
            # Prefer resources where we are not behind; break ties toward smaller ds then lexicographic
            key = (do - ds, ds, r[0], r[1])
            if best is None or key < best[0]:
                best = (key, r)
        return best[1]

    target = best_target()
    if target is None:
        # deterministic corner pressure
        tx, ty = (0, h - 1) if (ox + oy) > (sx + sy) else (w - 1, 0)
        target = (tx, ty)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        np = (nx, ny)
        # Goal: approach target; ensure we don't give opponent easier contest
        ds_next = md(np, target)
        do_curr = md(op, target)
        # approximate opponent response: compare our next distance vs opponent current distance
        contest_bias = (do_curr - ds_next)  # higher is better
        # avoid getting too close to opponent unless also reducing target distance a lot
        sep = md(np, op)
        close_pen = -2 if sep <= 1 else 0
        # slight edge penalty to reduce corner trap swings late-game
        edge_pen = -0.03 * (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        # primary: improve contest; secondary: reduce own distance; tertiary: deterministic tie-break
        val = (contest_bias * 10) - ds_next + close_pen + edge_pen
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]