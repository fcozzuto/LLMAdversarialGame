def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def wall_score(x, y):
        # higher means safer away from edges
        dx = x if x < w - 1 - x else w - 1 - x
        dy = y if y < h - 1 - y else h - 1 - y
        return (dx if dx < dy else dy)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy  # engine would keep in place
        d = cheb(nx, ny, ox, oy)
        if pursuer:
            # minimize distance; tie-breaker prefers moving "diagonally" to reach quicker and central-ish
            key = (d, -((nx != sx and ny != sy) or 0), -wall_score(nx, ny), nx, ny)
            # choose smallest key
        else:
            # maximize distance; tie-breaker prefers safer from walls; deterministic on coords
            key = (-d, -wall_score(nx, ny), nx, ny)
        if best is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]