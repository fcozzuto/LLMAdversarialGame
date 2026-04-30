def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # All 9-neighborhood deltas
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0,  0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    # Candidate moves excluding obstacles and off-grid
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

    # Chebyshev distance
    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Filter resources in-bounds
    res = []
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
        except:
            continue
        if inb(rx, ry) and (rx, ry) not in obstacles:
            res.append((rx, ry))

    # If resources exist, prioritize getting closer to nearest resource, but avoid moving away from opponent too much
    target = None
    if res:
        bestd = 10**9
        for rx, ry in res:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                target = (rx, ry)

    # Scoring for each candidate move
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy, nx, ny in cand:
        score = 0

        # Move toward target resource
        if target is not None:
            score += -(cheb(nx, ny, target[0], target[1]))

        # Stay closer to center to avoid being cornered
        cx, cy = w // 2, h // 2
        score += -(abs(nx - cx) + abs(ny - cy))

        # Avoid getting too close to opponent to prevent blocking; prefer keeping distance
        odx, ody = ox - nx, oy - ny
        manh = abs(odx) + abs(ody)
        score += - (manh // 2)

        # Avoid known obstacles proximity bonus if adjacent to obstacle? small bias
        for oxi, oyi in obstacles:
            if max(abs(nx - oxi), abs(ny - oyi)) == 1:
                score -= 1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]