def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Defensive switch: pick a resource where we can secure first (or deny by maximizing opponent delay)
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in resources:
            return [dx, dy]

        move_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            self_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)

            # If we can arrive first (or tie), push strongly; else choose the one we least lose.
            diff = opp_t - self_t  # positive => we beat opponent
            # Extra tie-breaker: prefer closer resources overall; and avoid resources that both can reach quickly.
            score = (diff * 1000) - self_t * 3
            if diff < 0:
                score = (diff * 1000) - self_t  # still deterministic, but denies by making diff as large as possible
            move_best = score if score > move_best else move_best

        if move_best > best_score:
            best_score = move_best
            best_move = [dx, dy]

    return best_move