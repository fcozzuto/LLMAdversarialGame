def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in self_role) or ("evader" in opp_role and "purs" not in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x, y, a, b):
        dx, dy = x - a, y - b
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if self_is_evader:
        far_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_opp = man(nx, ny, ox, oy)
            d_corner = man(nx, ny, far_corner[0], far_corner[1])
            # Primary: increase distance from pursuer; Secondary: head to far corner.
            v = d_opp * 4 + d_corner
            if v > bestv or (v == bestv and (dx, dy) == (-1, -1)):
                bestv = v
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]
    else:
        # Pursuer: chase with obstacle-aware fallback to corners to avoid deadlocks near obstacles.
        near_corner = min(corners, key=lambda c: man(c[0], c[1], ox, oy))
        best = None
        bestv = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            # If multiple equal distances, bias toward a corner (often helps trap lines against wall-runners).
            v = d * 10 + man(nx, ny, near_corner[0], near_corner[1]) // 2
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]