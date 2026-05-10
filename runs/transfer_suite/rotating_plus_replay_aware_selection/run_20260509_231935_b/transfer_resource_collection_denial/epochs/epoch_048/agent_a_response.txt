def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = set()
    for p in resources:
        if p and len(p) >= 2:
            res.add((p[0], p[1]))
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not res:
        return [0, 0]

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        dres = 10**9
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            d = cheb(nx, ny, rx, ry)
            if d < dres:
                dres = d

        dopp = cheb(nx, ny, ox, oy)

        # Prefer closer resources; if tie, prefer moving away from opponent.
        # Deterministic tie-break by dx, then dy.
        score = (-dres, dopp, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move