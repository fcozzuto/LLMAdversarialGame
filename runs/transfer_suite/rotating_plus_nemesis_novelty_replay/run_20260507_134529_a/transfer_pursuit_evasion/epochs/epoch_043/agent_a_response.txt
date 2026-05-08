def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" not in self_role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m

    def min_obs_d2(x, y):
        if not obstacles:
            return 10**9
        best = 10**9
        for (px, py) in obstacles:
            d = dist2(x, y, px, py)
            if d < best:
                best = d
        return best

    def wall_pressure(x, y):
        # closer to center is "safer"; closer to wall is "more constrained"
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return dist2(x, y, cx, cy)

    best_move = [0, 0]
    best_score = -10**18 if not self_is_evader else -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        mod = min_obs_d2(nx, ny)
        wp = wall_pressure(nx, ny)

        if self_is_evader:
            score = d + 0.35 * mob + 0.02 * mod + 0.01 * wp
        else:
            # pursuer: reduce distance, keep mobility, avoid squeezing into obstacles
            score = (-d) + 0.35 * mob + 0.02 * mod - 0.01 * wp

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]