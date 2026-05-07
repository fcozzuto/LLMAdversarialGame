def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    ox, oy = observation["opponent_position"]

    obst = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def best_for_next(nx, ny):
        best = None
        for rx, ry in resources:
            my_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)
            # Prefer resources we can secure before opponent; otherwise, prefer least-bad contest.
            secure = 1 if my_t < opp_t else 0
            gap = opp_t - my_t
            # Secondary: closer to us, and then deterministic by coordinates.
            key = (secure, gap, -my_t, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[0]

    # Evaluate moves; choose best score deterministically.
    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            nx, ny = sx, sy
            dx, dy = 0, 0
        score = best_for_next(nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move