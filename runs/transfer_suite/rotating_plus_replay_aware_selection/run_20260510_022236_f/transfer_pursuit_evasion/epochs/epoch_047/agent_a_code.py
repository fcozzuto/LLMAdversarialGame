def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.append((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_penalty(x, y):
        if not obs:
            return 0
        best = 10**9
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        if best == 0:
            return -10**7
        if best == 1:
            return -80
        if best == 2:
            return -25
        return 0

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            return sx, sy
        return nx, ny

    if is_evader:
        target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        tx, ty = target_corner
        best_score = -10**18
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = clamp_move(dx, dy)
            dist_to_p = abs(nx - ox) + abs(ny - oy)
            dist_to_t = abs(nx - tx) + abs(ny - ty)
            # Prefer moving away from pursuer while progressing toward the farthest corner.
            score = (dist_to_p * 5) - (dist_to_t * 1.2) + obs_penalty(nx, ny)
            if score > best_score:
                best_score, best_move = score, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # Pursuer: chase directly, but bias to reduce distance while avoiding obstacles.
        best_score = -10**18
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = clamp_move(dx, dy)
            dist = abs(nx - ox) + abs(ny - oy)
            # If capture is possible with radius 0, we hard-prioritize exact landing.
            capture_bonus = 10**6 if dist == 0 else 0
            score = (-dist * 10) + capture_bonus + obs_penalty(nx, ny)
            if score > best_score:
                best_score, best_move = score, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]