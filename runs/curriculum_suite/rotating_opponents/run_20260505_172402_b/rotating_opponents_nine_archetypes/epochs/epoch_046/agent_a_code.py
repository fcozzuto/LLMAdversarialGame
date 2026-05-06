def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    if not resources:
        # Hold center-ish away from opponent deterministically
        targets = [(w - 1, h - 1), (0, h - 1), (w - 1, 0), (0, 0)]
        tx, ty = targets[0]
        best = (10**9, None, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d_from_opp = cheb(nx, ny, ox, oy)
            d_from_corner = cheb(nx, ny, tx, ty)
            key = (-d_from_opp, d_from_corner, dx, dy)
            if best[1] is None or key < (best[0], 0, best[2], best[3]):
                best = (key[0], key[1], dx, dy)
        return [best[2], best[3]]

    best_key = None
    best_move = [0, 0]
    # Choose resource race: minimize our distance, maximize lead over opponent, tie-break by staying farther from opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dmin = 10**9
        lead_best = -10**9
        d_opp_closest = 10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            if d_self < dmin:
                dmin = d_self
            d_opp = cheb(ox, oy, rx, ry)
            if d_opp < d_opp_closest:
                d_opp_closest = d_opp
            # Positive if we are closer (race lead)
            lead = d_opp - d_self
            if lead > lead_best:
                lead_best = lead
        # Prefer moves that secure/improve lead; otherwise just reduce our approach distance.
        # Deterministic tie-break uses lexicographic of (lead_best desc, dmin asc, opp_dist desc, dx, dy).
        opp_dist = cheb(nx, ny, ox, oy)
        key = (-lead_best, dmin, -opp_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]