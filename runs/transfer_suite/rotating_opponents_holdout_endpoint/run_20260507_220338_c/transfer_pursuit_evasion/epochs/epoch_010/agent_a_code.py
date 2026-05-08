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
    pursuer = ("pursuer" in role) or ("hunter" in role)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = None
    best_score = None

    for dx, dy, nx, ny in legal:
        d_opp = cheb(nx, ny, ox, oy)

        # Heuristic to avoid getting squeezed against walls/obstacle clusters
        adj_block = 0
        for ax, ay in dirs:
            tx, ty = nx + ax, ny + ay
            if not in_bounds(tx, ty) or (tx, ty) in blocked:
                adj_block += 1

        # If evading, bias toward far corner; if pursuing, bias toward near corner
        bias_corner = cheb(nx, ny, *(far_corner if not pursuer else near_corner))

        # Score: higher is better for evader; lower is better for pursuer, unify by multiplying
        # pursuer wants smaller d_opp => score should be higher when d_opp is smaller after transform
        if pursuer:
            score = (-d_opp) - (0.15 * bias_corner) - (0.05 * adj_block)
        else:
            score = (d_opp) - (0.15 * bias_corner) - (0.05 * adj_block)

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    return [int(best[0]), int(best[1])]