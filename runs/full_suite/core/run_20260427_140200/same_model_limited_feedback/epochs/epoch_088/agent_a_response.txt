def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])

    obs_set = set((x, y) for x, y in obstacles)
    move_opts = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_move():
        best = None
        best_val = None
        for dx, dy in move_opts:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue

            if not resources:
                # fallback: head toward the center
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                our = dist(nx, ny, cx, cy)
                opp = dist(ox, oy, cx, cy)
                val = (opp - our) * 10 - our
            else:
                val = -10**18
                for rx, ry in resources:
                    d_our = dist(nx, ny, rx, ry)
                    d_opp = dist(ox, oy, rx, ry)
                    advantage = d_opp - d_our
                    bonus = 5000 if nx == rx and ny == ry else 0
                    cand = bonus + advantage * 50 - d_our
                    if cand > val:
                        val = cand

            if best is None or val > best_val:
                best = [dx, dy]
                best_val = val
        return best if best is not None else [0, 0]

    return best_move()