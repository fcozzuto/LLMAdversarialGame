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

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    moves = [(0, 0), (1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic tie-break order: closer to goal direction first, then lexicographic.
    if self_is_evader:
        # Evader: maximize distance, but also try to break opponent's approach by biasing away from the direct step.
        # Direct step direction (sign only).
        ddx = 0 if ox == sx else (1 if ox > sx else -1)
        ddy = 0 if oy == sy else (1 if oy > sy else -1)

        best_move = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = md(nx, ny, ox, oy)
            # Penalize continuing in opponent's direct approach direction.
            approach_dot = (dx == ddx) + (dy == ddy)
            # Prefer increasing distance most; small secondary preference to move toward farthest corner.
            corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
            far_corner = max(corners, key=lambda c: md(c[0], c[1], ox, oy))
            corner_bonus = -md(nx, ny, far_corner[0], far_corner[1])
            key = (d, -approach_dot, corner_bonus, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move
    else:
        # Pursuer: minimize distance, strongly bias capture (same cell), avoid blocked moves.
        best_move = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = md(nx, ny, ox, oy)
            # If can capture immediately (capture_radius 0): choose it.
            capture = 1 if (nx == ox and ny == oy) else 0
            # Small bias toward aligning with opponent to reduce future escape.
            adx = 0 if ox == nx else (1 if ox > nx else -1)
            ady = 0 if oy == ny else (1 if oy > ny else -1)
            align = (dx == adx) + (dy == ady)
            # Prefer smaller distance, then higher capture, then higher alignment, deterministic tie-break.
            key = (capture, -d, align, -dx, -dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move