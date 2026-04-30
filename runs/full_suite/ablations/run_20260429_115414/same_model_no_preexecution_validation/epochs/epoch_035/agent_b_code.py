def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = 0, 0
    else:
        # Pick resource we can secure: maximize (opp_dist - self_dist), tie-break by self closer.
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (do - ds, -ds, -((rx + ry) % 3))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # Local obstacle-aware move selection for the chosen target.
    def obstacle_penalty(x, y):
        if (x, y) in obs:
            return 1000
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    pen += 6
        return pen

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine will keep us in place
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Encourage reaching the target while also denying: increase relative advantage; avoid obstacles.
        score = (do2 - ds2) * 50 - ds2 * 3 + (0 if (nx, ny) == (tx, ty) else 0) - obstacle_penalty(nx, ny)
        # Slightly prefer moves that increase distance from opponent to reduce interference.
        score += (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)) * 1.5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]