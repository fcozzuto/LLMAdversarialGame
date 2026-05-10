def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list if p is not None and len(p) >= 2}
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(p):
        return p is not None and len(p) >= 2 and 0 <= p[0] < w and 0 <= p[1] < h and (p[0], p[1]) not in obstacles

    res = [tuple(r) for r in resources if inb(r)]
    if not res:
        return [0, 0]

    # Target selection: maximize current advantage (opponent farther than us). Tie-break by closer to us.
    best_t = None
    best_adv = None
    for rx, ry in res:
        sa = md(sx, sy, rx, ry)
        oa = md(ox, oy, rx, ry)
        adv = oa - sa
        if best_adv is None or adv > best_adv or (adv == best_adv and (sa < md(sx, sy, best_t[0], best_t[1]) or (sa == md(sx, sy, best_t[0], best_t[1]) and (rx, ry) < best_t))):
            best_adv = adv
            best_t = (rx, ry)

    tx, ty = best_t
    # One-step policy: prefer moves that improve our reach while keeping us ahead of opponent for that target.
    # Score tuple: (is_target_tied_or_losing, our_dist, opp_dist, tie_break_dir)
    best = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = md(nx, ny, tx, ty)
        d_opp = md(ox, oy, tx, ty)
        losing = 1 if d_self >= d_opp else 0
        # Secondary tie-break: also slightly prefer decreasing distance to the target itself.
        val = (losing, d_self, d_opp, dx, dy)
        if best is None or val < best:
            best = val
            best_move = (dx, dy)

    # If all moves end up not improving relative position, pivot to best advantage resource from the new position.
    # (Makes a meaningful strategic change vs pure greedy.)
    nx, ny = sx + best_move[0], sy + best_move[1]
    cur_opp_d = md(ox, oy, tx, ty)
    cur_self_d = md(nx, ny, tx, ty)
    if cur_self_d >= cur_opp_d:
        best2 = None
        best_move2 = best_move
        for dx, dy in dirs:
            x2, y2 = sx + dx, sy + dy
            if not ok(x2, y2):
                continue
            for rx, ry in res:
                ds = md(x2, y2, rx, ry)
                do = md(ox, oy, rx, ry)
                # Prefer resources where we are ahead after the move.
                losing = 1 if ds >= do else 0
                val = (losing, ds, do, (rx, ry), dx, dy)
                if best2 is None or val < best2:
                    best2 = val
                    best_move2 = (dx, dy)
        return [best_move2[0], best_move2[1]]

    return [best_move[0], best_move[1]]