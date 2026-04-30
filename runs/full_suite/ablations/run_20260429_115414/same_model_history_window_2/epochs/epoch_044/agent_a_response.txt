def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestv, bestm = None, (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -cheb(nx, ny, cx, cy) - 0.001 * cheb(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv, bestm = v, (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    bestv, bestm = None, (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose the target resource we'd likely take next, but prefer ones that keep the opponent farther behind.
        my_d_best = None
        opp_d_for_best = None
        for tx, ty in resources:
            my_d = cheb(nx, ny, tx, ty)
            if my_d_best is None or my_d < my_d_best or (my_d == my_d_best and cheb(ox, oy, tx, ty) > opp_d_for_best):
                my_d_best = my_d
                opp_d_for_best = cheb(ox, oy, tx, ty)

        # Prefer being closer to an available resource, and (importantly) being relatively closer than the opponent.
        # Add small bias to reduce staying in place.
        v = (opp_d_for_best - my_d_best) - 0.1 * my_d_best - 0.01 * cheb(nx, ny, sx, sy)
        if bestv is None or v > bestv:
            bestv, bestm = v, (dx, dy)

    return [int(bestm[0]), int(bestm[1])]