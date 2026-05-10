def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    role = (observation.get("self_role") or "").lower()
    pursuer = "pursuer" in role

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def near_obs_pen(x, y):
        if not obs:
            return 0
        best = 10**9
        for ax, ay in obstacles:
            dx, dy = x - ax, y - ay
            d = dx * dx + dy * dy
            if d < best:
                best = d
                if best <= 1:
                    break
        if best <= 1: return 1000
        if best <= 4: return 80
        if best <= 9: return 25
        return 0

    def wall_score(x, y):
        # keep away from walls to avoid corner traps; deterministic tie-break
        return min(x, y, w - 1 - x, h - 1 - y)

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        d2 = dist2(nx, ny)
        man = abs(nx - ox) + abs(ny - oy)
        nobs = near_obs_pen(nx, ny)
        ws = wall_score(nx, ny)

        # Main objective: approach if pursuer, evade if evader
        # Extra: prefer moves that "push" along the larger separation axis (good vs zigzags).
        adx, ady = abs(nx - ox), abs(ny - oy)
        axis_push = -adx if adx > ady else -ady  # pursuer wants more closeness; evader later flips

        val = (d2 if pursuer else -d2)
        val += nobs
        if pursuer:
            val += -0.1 * ws  # slightly prefer center when chasing to avoid obstacles
            val += axis_push * 0.01
        else:
            val += 0.1 * (-ws)  # prefer center when evading
            val += (-axis_push) * 0.01

        if best is None or val < best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]