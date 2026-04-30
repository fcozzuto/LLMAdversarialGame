def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                sx, sy = nx, ny
                break
        else:
            return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return list(best[1]) if best else [0, 0]

    best_move = None
    # Prefer moves that maximize (opponent distance - our distance) to the best resource we can contest.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        max_adv = None
        best_self_dist = None
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self
            if max_adv is None or adv > max_adv or (adv == max_adv and d_self < best_self_dist):
                max_adv = adv
                best_self_dist = d_self
        # Secondary: avoid giving opponent a close immediate contest (minimize our resulting distance to the best resource).
        # Tertiary tie-break: deterministic preference for moves toward top-left in order.
        cand = (-(max_adv), best_self_dist, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand

    if best_move is None:
        return [0, 0]
    return [best_move[2], best_move[3]]