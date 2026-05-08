def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    r = int(observation.get("capture_radius", 0) or 0)

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in blocked:
                m += 1
        return m

    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue

        d = cheb(nx, ny, ox, oy)
        if pursuer and d <= r:
            return [dx, dy]

        m = mobility(nx, ny)
        if pursuer:
            # Greedy closing + prefer low mobility to limit opponent escape routes
            score = (-d) * 1000 + (-m)
            # Wall-alignment bias: reduce distance more aggressively when moving toward same x/y side
            if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
                score += -2
        else:
            # Fleeing: maximize distance and mobility; avoid moving into "tight" corridors
            score = (d) * 1000 + (m)
            if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
                score += 2  # wall-run: hug walls deterministically

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]