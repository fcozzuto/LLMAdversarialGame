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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if resources:
        best = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer positive advantage; break ties by closer to self, then lexicographically.
            key = (-(do - ds), ds, tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        tx, ty = best[1]
        best_move = (10**9, 10**9, 0, 0)  # (adv_to_target, dist_to_target, dx, dy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d1 = cheb(nx, ny, tx, ty)
            # Anticipate opponent pressure on same target from their current position.
            do = cheb(ox, oy, tx, ty)
            adv = -(do - d1)  # smaller is better
            cand = (adv, d1, dx, dy)
            if cand < best_move:
                best_move = cand
        dx, dy = best_move[2], best_move[3]
        return [int(dx), int(dy)]

    # No resources: move toward a point closer to opponent's corner but also toward midline.
    if (ox + oy) > (w - 1):
        tx, ty = 0, 7
    else:
        tx, ty = w - 1, 0

    best_move = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer also reducing distance to opponent to deny space.
        dp = cheb(nx, ny, ox, oy)
        cand = (d, dp, dx, dy)
        if cand < best_move:
            best_move = cand
    dx, dy = best_move[2], best_move[3]
    return [int(dx), int(dy)]