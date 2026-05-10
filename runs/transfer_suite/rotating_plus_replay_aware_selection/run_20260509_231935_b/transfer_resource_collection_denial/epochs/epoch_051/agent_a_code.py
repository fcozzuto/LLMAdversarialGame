def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = set()
    for p in resources:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                res.add((x, y))
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = 10**18

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        if (nx, ny) in res:
            score = -1000000  # immediate pickup
        else:
            mind = 10**9
            for rx, ry in res:
                if (rx, ry) in obs:
                    continue
                d = cheb(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            score = mind * 1000

        # tiebreakers: avoid drifting backwards; keep deterministic
        score += (dx * dx + dy * dy)  # prefer smaller moves
        score += (abs(nx - (w - 1)) + abs(ny - (h - 1))) * 0.001  # slight pull to far corner

        if score < best_score or (score == best_score and (dx, dy) > best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]