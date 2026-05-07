def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def dist(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    best_move = (0, 0)
    best_util = (-10**9, 0, 0)

    # Deterministic preference order if utilities match
    move_order = {m: i for i, m in enumerate(moves)}

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        move_best = (-2, -10**9, -10**9)  # (state, margin, -st)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = dist(nsx, nsy, rx, ry)
            ot = dist(ox, oy, rx, ry)
            margin = ot - st

            if st < ot:
                util = (1, margin, -st)     # we get it first
            elif st == ot:
                util = (0, 0, -st)         # tie: value earlier collection slightly
            else:
                util = (-1, margin, -ot)  # opponent earlier; still consider best chance

            if util > move_best:
                move_best = util
            elif util == move_best:
                # tie-break on closer target (smaller st), then deterministic
                if st < dist(nsx, nsy, rx, ry):
                    move_best = util

        if move_best > best_util:
            best_util = move_best
            best_move = (mdx, mdy)
        elif move_best == best_util:
            if move_order[(mdx, mdy)] < move_order[best_move]:
                best_move = (mdx, mdy)

    return [best_move[0], best_move[1]]