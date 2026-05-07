def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1),
             (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def dist(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        return dx if dx >= 0 else -dx if dy == 0 else max(dx if dx >= 0 else -dx, dy if dy >= 0 else -dy)
    # safer dist:
    def turns(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_score = {}
    # Prefer resources we can reach at least as fast; otherwise minimize our arrival time.
    best_mv = (0, 0)
    best_key = None
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        worst_key_for_move = None
        move_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ot = turns(ox, oy, rx, ry)
            st = turns(nsx, nsy, rx, ry)

            # If we get there no later, great. If later, heavily penalize.
            if st <= ot:
                # tie-break by how much earlier we are, then shorter st.
                key = (0, -((ot - st) * 1000 + (ot - st)), st)
            else:
                # we may still collect if opponent denies; prefer smallest gap (least worse).
                gap = st - ot
                key = (1, gap, st)

            if worst_key_for_move is None or key < worst_key_for_move:
                worst_key_for_move = key
                move_best = (rx, ry, ot, st)

        # Secondary: choose move that reduces closest resource distance (and optionally blocks).
        if move_best is None:
            continue
        rx, ry, ot, st = move_best
        nearest_self = min(turns(nsx, nsy, r[0], r[1]) for r in resources if tuple(r) not in obstacles)
        nearest_opp = min(turns(ox, oy, r[0], r[1]) for r in resources if tuple(r) not in obstacles)
        # Encourage being closer than opponent overall (even if no guaranteed win).
        key_total = (worst_key_for_move[0],
                     worst_key_for_move[1],
                     worst_key_for_move[2],
                     (nearest_self - nearest_opp),
                     st,
                     mdx, mdy)
        if best_key is None or key_total < best_key:
            best_key = key_total
            best_mv = (mdx, mdy)

    return [int(best_mv[0]), int(best_mv[1])]