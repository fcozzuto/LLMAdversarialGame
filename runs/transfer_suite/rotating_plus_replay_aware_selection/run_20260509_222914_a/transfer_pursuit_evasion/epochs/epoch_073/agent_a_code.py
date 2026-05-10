def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def obst_cost(nx, ny):
        if (nx, ny) in obstacles:
            return 1e7
        best = 10**9
        for x, y in obstacles:
            d = abs(nx - x) + abs(ny - y)
            if d < best:
                best = d
        if best == 10**9:
            return 0.0
        if best == 0:
            return 1e7
        if best <= 1:
            return 1000.0
        return 50.0 / best

    def corner_score(nx, ny):
        # For evader: prefer far from pursuer by pushing toward farthest corner from opponent.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = -1
        for cx, cy in corners:
            d_corner = abs(cx - ox) + abs(cy - oy)
            d_me = abs(nx - cx) + abs(ny - cy)
            best = max(best, d_corner - 0.35 * d_me)
        return best

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        dto = abs(nx - ox) + abs(ny - oy)
        c = obst_cost(nx, ny)

        if pursuer:
            # Aggressive: minimize distance, strongly avoid obstacles, keep moving (prefer progress).
            val = dto + 0.15 * abs(nx - sx) + c
            better = (best_val is None) or (val < best_val) or (val == best_val and (dx, dy) < best)
        else:
            # Evader: maximize distance and steer to corner opposite opponent; avoid obstacles.
            val = -dto + -0.03 * (nx - sx) + -0.03 * (ny - sy) - corner_score(nx, ny) + c
            better = (best_val is None) or (val < best_val) or (val == best_val and (dx, dy) < best)

        if better:
            best = (dx, dy)
            best_val = val

    return [int(best[0]), int(best[1])]