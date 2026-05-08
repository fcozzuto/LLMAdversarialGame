def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in srole) or ("chase" in srole) or ("seeker" in srole) or ("catch" in srole)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y):
        # Chebyshev distance matches diagonal grid movement
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def corner_bias(x, y):
        # pursuer: prefer smaller (closer to corners generally), evader: prefer larger
        best = None
        for cx, cy in corners:
            d = abs(x - cx) + abs(y - cy)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_delta = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = dist(nx, ny)
        cb = corner_bias(nx, ny)
        # Add a small tie-breaker to avoid oscillations into corners when not beneficial.
        # For pursuer: smaller distance is better; for evader: larger distance is better.
        if is_pursuer:
            score = (-d * 1000) + (cb * -2)  # keep away from corners only slightly
        else:
            score = (d * 1000) + (cb * 2)
        if best_score is None or score > best_score:
            best_score = score
            best_delta = [dx, dy]

    return best_delta