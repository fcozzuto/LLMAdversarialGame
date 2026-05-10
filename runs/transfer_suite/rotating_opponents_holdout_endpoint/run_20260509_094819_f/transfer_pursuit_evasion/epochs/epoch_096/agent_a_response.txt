def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    pursuer = ("pursur" in sr) or ("chaser" in sr) or ("hunter" in sr) or ("tag" in sr) or ("pursuer" in sr)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: cheb(sx, sy, c[0], c[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        d = cheb(nx, ny, ox, oy)
        if pursuer:
            # Prefer reducing distance; nudge toward corner to break ties.
            score = -d
            score += -0.05 * cheb(nx, ny, target_corner[0], target_corner[1])
        else:
            # Prefer increasing distance; if tied, move toward farthest corner from pursuer.
            score = d
            far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
            score += 0.05 * cheb(nx, ny, far_corner[0], far_corner[1])

        if best_val is None or (score > best_val) or (score == best_val and (dx, dy) < best):
            best_val = score
            best = (dx, dy)

    if best is None:
        # Must be deterministic; if trapped by obstacles, stay.
        return [0, 0]
    return [best[0], best[1]]