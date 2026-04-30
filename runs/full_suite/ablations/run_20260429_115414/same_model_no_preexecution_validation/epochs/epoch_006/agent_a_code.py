def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    def nearest_obstacle_dist(x, y):
        if not obstacles:
            return 99
        best = 99
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best

    # Pick a contested resource: maximize (opponent distance - our distance)
    if resources:
        best_r = None
        best_val = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; also avoid extremely far targets
            val = (do - ds) * 10 - ds
            if best_val is None or val > best_val or (val == best_val and (ds < cheb(sx, sy, best_r[0], best_r[1]) if best_r else True)):
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # No resources: move toward a safe-ish central point
        tx, ty = (w // 2) - 1 if w % 2 == 0 else w // 2, (h // 2) - 1 if h % 2 == 0 else h // 2

    # Choose move that most improves our contest score for (tx,ty)
    best = None
    for dx, dy, nx, ny in legal_moves:
        ds_now = cheb(nx, ny, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        # Encourage reducing our distance and, secondarily, not letting opponent be closer than us
        our_score = (do_now - ds_now) * 10 - ds_now
        # Obstacle avoidance: prefer staying away from walls/obstacles
        obs_dist = nearest_obstacle_dist(nx, ny)
        # Small deterministic tie-breaker: lexicographic on (dx,dy)
        tieb = (obs_dist, -abs(nx - sx) - abs(ny - sy), -cheb(nx, ny, ox, oy))
        score = (our_score, tieb[0], tieb[1], tieb[2], -dx, -dy)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]