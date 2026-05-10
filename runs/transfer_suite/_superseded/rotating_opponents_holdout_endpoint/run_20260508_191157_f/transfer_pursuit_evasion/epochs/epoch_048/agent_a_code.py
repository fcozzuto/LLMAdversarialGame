def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    env = observation.get("environment_name", "")
    if env != "pursuit_evasion":
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def clamp(x, y):
        return (0 if x < 0 else (w - 1 if x >= w else x),
                0 if y < 0 else (h - 1 if y >= h else y))

    def cheb(x, y):
        ax, ay = x - ox, y - oy
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def wall_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def obstacle_risk(x, y):
        # Higher = worse; strongly avoid landing on obstacles or adjacent to them.
        if (x, y) in obs:
            return 10**6
        r = 0
        for nx in (x - 1, x, x + 1):
            for ny in (y - 1, y, y + 1):
                if (nx, ny) in obs:
                    man = abs(nx - x) + abs(ny - y)
                    r += 40 if man == 0 else (16 if man == 1 else 6)
        return r

    # Evader: maximize distance; also prefer larger clearance from obstacles and walls.
    # Pursuer: minimize distance; avoid walls/obstacles that block progress.
    targets = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Deterministic corner preference: pick the corner farthest from opponent.
    best_corner = max(targets, key=lambda t: cheb(t[0], t[1]))

    best_move = None
    best_val = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        risk = obstacle_risk(nx, ny)
        dist = cheb(nx, ny)

        # Bias direction: evader drifts toward safer far corner; pursuer drifts toward opponent side.
        drift = cheb(nx, best_corner[0],) if False else 0  # keep deterministic structure
        if is_evader:
            # Prefer larger distance and being away from obstacles/walls; slight attraction to farthest corner.
            drift = cheb(nx, ny)
            toward_corner = - (abs(best_corner[0] - nx) + abs(best_corner[1] - ny))
            val = dist * 1000 - risk * 3 + wall_dist(nx, ny) * 6 + toward_corner * 0.5
        elif is_pursuer:
            # Prefer reducing distance; avoid high risk; keep some mobility near center away from walls.
            val = -dist * 1000 - risk * 3 + (7 - wall_dist(nx, ny)) * 0.2
        else:
            # Fallback: assume evader if role unclear.
            toward_corner = - (abs(best_corner[0] - nx) + abs(best_corner[1] - ny))
            val = dist * 1000 - risk * 3 + wall_dist(nx, ny) * 6 + toward_corner * 0.5

        if best_val is None:
            best_val = val
            best_move = (dx, dy)
        else:
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]