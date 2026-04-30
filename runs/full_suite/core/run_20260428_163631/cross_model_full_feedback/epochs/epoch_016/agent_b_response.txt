def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # All 9-neighborhood deltas, excluding staying still will handle below
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0,  0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    # Build candidate moves excluding obstacles and off-grid; we may allow stay in place as fallback
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Helper: Chebyshev distance
    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # If resources present, try to move toward nearest resource but avoid giving opponent immediate advantage
    target = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                target = (rx, ry)

    # Evaluate simple heuristic: prefer moves that approach closest resource, then avoid stepping into cells near opponent
    best_move = None
    best_score = -10**9

    for dx, dy, nx, ny in cand:
        score = 0

        # Proximity to resource
        if target is not None:
            d = cheb(nx, ny, target[0], target[1])
            score += max(0, 10 - d)

        # Proximity to opponent: discourage getting too close unless you gain advantage
        od = cheb(nx, ny, ox, oy)
        if od <= 1:
            score -= 5  # avoid immediate clash

        # Obstacles avoided already; small preference to center area
        center_x, center_y = w // 2, h // 2
        score -= abs(nx - center_x) + abs(ny - center_y)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]