def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)
    role = (observation.get("self_role") or "").lower()
    is_pursuer = "pursuer" in role

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def penalty_obstacles(x, y):
        if not obs:
            return 0
        best = 10**9
        for ax, ay in obstacles:
            dx, dy = x - ax, y - ay
            d = dx * dx + dy * dy
            if d < best:
                best = d
                if best == 0:
                    break
        if best <= 1:
            return 60
        if best <= 4:
            return 18
        if best <= 9:
            return 7
        return 0

    def wall_bias(x, y):
        # Prefer keeping distance from nearest wall (fewer dead-ends with wall-runner patterns)
        return min(x, y, w - 1 - x, h - 1 - y)

    best_move = [0, 0]
    best_val = None

    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            ddx, ddy = 0, 0

        d2 = dist2(nx, ny)
        mob = 0
        for mdx, mdy in deltas:
            tx, ty = nx + mdx, ny + mdy
            if in_bounds(tx, ty) and (tx, ty) not in obs:
                mob += 1

        # Score: pursuer tries to minimize distance and avoid obstacles; evader tries to maximize distance while staying mobile
        p_obs = penalty_obstacles(nx, ny)
        wb = wall_bias(nx, ny)

        if is_pursuer:
            val = (-d2) + 0.8 * mob + 0.05 * wb - p_obs * 1.2
            better = (best_val is None) or (val > best_val) or (val == best_val and (ddx, ddy) < (best_move[0], best_move[1]))
        else:
            val = (d2) + 0.9 * mob + 0.03 * wb - p_obs * 1.0
            better = (best_val is None) or (val > best_val) or (val == best_val and (ddx, ddy) < (best_move[0], best_move[1]))

        if better:
            best_val = val
            best_move = [ddx, ddy]

    return best_move