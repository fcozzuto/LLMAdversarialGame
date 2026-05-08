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

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def legal_moves():
        res = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in blocked:
                res.append((dx, dy, nx, ny))
        return res

    moves = legal_moves()
    if not moves:
        return [0, 0]

    # Avoid near-deadlocks: penalize moves that have fewer onward options.
    def onward_count(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    # Target corners deterministically to escape zigzags as evader.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Choose best corner based on current opponent position and whether we're pursuer/evader.
    if pursuer:
        # As pursuer, we don't want corners; we want to close.
        target_corner = None
    else:
        # As evader, prefer farthest corner; tie-break by deterministic ordering.
        farthest = corners[0]
        bestd = cheb(corners[0][0], corners[0][1], ox, oy)
        for c in corners[1:]:
            d = cheb(c[0], c[1], ox, oy)
            if d > bestd:
                bestd, farthest = d, c
        target_corner = farthest

    best = None
    best_val = None

    for dx, dy, nx, ny in moves:
        dist = cheb(nx, ny, ox, oy)

        # If we're pursuer, prefer smallest distance; if evader, prefer largest distance.
        primary = -dist if pursuer else dist

        # Corner bias for evader to keep escape direction coherent.
        corner_term = 0
        if not pursuer:
            corner_term = -cheb(nx, ny, target_corner[0], target_corner[1])

        # Obstacle/space term: prefer moves with more onward options.
        space = onward_count(nx, ny)

        # Deterministic tie-break: use lexicographic move direction.
        tie = (dx, dy)

        # Compose value: pursuer maximizes primary; evader maximizes primary too, via sign.
        # Add small weights for space and corner to break ties without overriding distance.
        val = primary * 1000 + space * (1 if pursuer else 1) + corner_term * 0.5

        if best is None or val > best_val or (val == best_val and tie > best[0]):
            best = (tie, dx, dy)
            best_val = val

    return [int(best[1]), int(best[2])]