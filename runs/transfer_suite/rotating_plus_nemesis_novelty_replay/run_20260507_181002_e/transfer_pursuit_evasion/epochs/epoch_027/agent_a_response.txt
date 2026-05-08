def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role) or ("tagger" in role)
    # If unsure, act like pursuer (usually better for capture points)
    if "evader" in role or "runner" in role:
        pursuer = False

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        d = abs(nx - ox) + abs(ny - oy)
        # obstacle-proxy: count blocked adjacent (prefer more freedom)
        blocked = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            tx, ty = nx + adx, ny + ady
            if not free(tx, ty):
                blocked += 1

        corner_bias = abs(far_corner[0] - nx) + abs(far_corner[1] - ny)
        # Deterministic tie-break: lexicographic on (dx, dy)
        score = 0
        if pursuer:
            score = -d - 0.05 * blocked + 0.001 * corner_bias
        else:
            score = d - 0.05 * blocked - 0.001 * corner_bias

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]