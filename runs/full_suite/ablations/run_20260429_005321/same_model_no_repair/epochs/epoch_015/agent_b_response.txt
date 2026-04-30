def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def pick_target(px, py):
        if not resources:
            return (w - 1, h - 1)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # For self: minimize ds-do (we are closer); for opponent: opposite via px/py swap effect handled below
            if (px, py) == (sx, sy):
                key = (ds - do, ds, rx, ry)
            else:
                key = (do - ds, do, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        if best is None:
            return (w - 1, h - 1)
        return (best[1], best[2])

    my_t = pick_target(sx, sy)
    opp_t = pick_target(ox, oy)

    # Decide whether to contest opponent's likely target
    my_ds = cheb(sx, sy, my_t[0], my_t[1])
    my_do = cheb(ox, oy, my_t[0], my_t[1])
    cont_ds = cheb(sx, sy, opp_t[0], opp_t[1])
    cont_do = cheb(ox, oy, opp_t[0], opp_t[1])

    target = opp_t if (cont_ds < cont_do) or (my_ds >= my_do and cont_ds <= my_ds) else my_t
    tx, ty = target

    best_mv = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Primary: reduce distance to chosen target; Secondary: avoid getting closer to opponent target line
        d = cheb(nx, ny, tx, ty)
        opp_target_dist = cheb(nx, ny, opp_t[0], opp_t[1])
        opp_adv = cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty)  # higher => we gain
        val = (d, -opp_adv, opp_target_dist, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_mv = (dx, dy)

    if best_mv is None:
        return [0, 0]
    return [int(best_mv[0]), int(best_mv[1])]