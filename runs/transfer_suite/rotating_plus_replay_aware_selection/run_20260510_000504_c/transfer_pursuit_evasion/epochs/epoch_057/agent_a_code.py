def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("escape" in self_role) or ("purs" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = (None, None)
    best_score = -10**9 if self_is_evader else 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic "blocked" handling

        dist = md(nx, ny, ox, oy)

        # Evader: maximize distance and move toward the farthest corner.
        # Pursuer: minimize distance and move toward the nearest corner to cut off.
        target_corner = max(corners, key=lambda c: md(c[0], c[1], ox, oy)) if self_is_evader else min(corners, key=lambda c: md(c[0], c[1], ox, oy))
        corner_dist = md(nx, ny, target_corner[0], target_corner[1])

        # Small penalty/bonus for alignment (reduces dithering).
        align = -(abs((nx - ox)) + abs((ny - oy))) if self_is_evader else (abs((nx - ox)) + abs((ny - oy)))

        # Deterministic score.
        if self_is_evader:
            score = dist * 10 + corner_dist * 1 + align * 0.01
            if score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            score = dist * 10 - corner_dist * 1 - align * 0.01
            if score < best_score:
                best_score = score
                best = (dx, dy)

    if best[0] is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]