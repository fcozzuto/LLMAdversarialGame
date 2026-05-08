def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    x0, y0 = observation.get("self_position", [0, 0]) or [0, 0]
    xo, yo = observation.get("opponent_position", [0, 0]) or [0, 0]
    x0, y0, xo, yo = int(x0), int(y0), int(xo), int(yo)

    obstacles = observation.get("obstacles", []) or []
    ox = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ox.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    is_evader = "evader" in role

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx, dy in dirs:
        nx, ny = x0 + dx, y0 + dy
        if in_bounds(nx, ny) and (nx, ny) not in ox:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    def cheb(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    best = None
    best_key = None

    for dx, dy, nx, ny in legal:
        dist = cheb(nx, ny, xo, yo)

        # Dead-end / obstacle density heuristic for staying mobile
        free_neighbors = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if in_bounds(tx, ty) and (tx, ty) not in ox:
                free_neighbors += 1

        # Boundary penalty discourages getting pinned by edges/obstacles
        boundary = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
        boundary_score = boundary  # larger is safer from corners

        # Corner targeting for evader: pick farthest corner from pursuer
        if is_evader:
            far_corner = max(corners, key=lambda c: cheb(c[0], c[1], xo, yo))
            corner_dist = cheb(nx, ny, far_corner[0], far_corner[1])
        else:
            corner_dist = 0

        # Deterministic tie-break favor diagonal progress
        tieb = (0 if dx == 0 and dy == 0 else 1, abs(dx), abs(dy), dx, dy)

        if is_evader:
            key = (-dist, corner_dist, free_neighbors, boundary_score, tieb)
        else:
            # pursuer: minimize distance, prefer moves that reduce free neighbors of evader when possible
            # (approx via increasing closeness and reducing our mobility a bit to avoid oscillation)
            key = (dist, 0 if free_neighbors >= 6 else 1, -free_neighbors, -boundary_score, tieb)

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]