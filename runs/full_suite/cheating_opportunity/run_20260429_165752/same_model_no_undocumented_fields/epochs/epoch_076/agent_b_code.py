def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

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

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # If no resources visible, head toward the more "central" side away from opponent.
    if not resources:
        tx, ty = (0, 0) if (ox + oy) > (sx + sy) else (w - 1, h - 1)
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            # Prefer shrinking distance to target while increasing opponent distance slightly.
            v = -(cheb(nx, ny, tx, ty)) + 0.2 * (cheb(nx, ny, ox, oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose move that maximizes our advantage over opponent for the best (most contested) resource.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        min_self = 10**9
        min_opp = 10**9
        # Also track the nearest resource to us after the move (tie-breaker).
        nearest = None

        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < min_self:
                min_self = ds
                nearest = (rx, ry)
            if do < min_opp:
                min_opp = do

        # Advantage is (opponent far - our close) across the closest resources.
        # Add a small penalty if the move increases our distance to the nearest resource.
        current_nearest = cheb(sx, sy, nearest[0], nearest[1]) if nearest else 0
        score = (min_opp - min_self) * 10.0 - (min_self - current_nearest) * 1.0

        # Obstacle-aware micro: prefer moves that keep us from being adjacent to obstacles too often.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1
        score -= adj_obs * 0.05

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]