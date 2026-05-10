def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("pursuer" in role) or ("pursuer" in opp_role) and ("evader" in role) == False
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_pen(x, y):
        if not obs:
            return 0
        best = 10**9
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        if best <= 0:
            return -10**6
        if best == 1:
            return -90
        if best == 2:
            return -25
        if best == 3:
            return -8
        return 0

    def corner_far_from(tgx, tgy):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestd = -1
        for cx, cy in corners:
            d = abs(cx - tgx) + abs(cy - tgy)
            if d > bestd:
                bestd = d
                best = (cx, cy)
        return best

    # Evader prefers moving toward the farthest corner from the pursuer; pursuer prefers reducing distance.
    target_corner = corner_far_from(ox, oy) if is_evader and not is_pursuer else corner_far_from(sx, sy)
    tx, ty = target_corner

    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_after = abs(nx - ox) + abs(ny - oy)
        # tie-breaker: keep heading (evader to corner, pursuer toward opponent)
        head = abs((tx - nx)) + abs((ty - ny)) if (is_evader and not is_pursuer) else 0
        score = 0
        if is_pursuer and not is_evader:
            score = (-d_after * 10) + (-(head) * 0.1) + obs_pen(nx, ny)
        else:
            score = (d_after * 10) + (-(head) * 0.6) + (-obs_pen(nx, ny) * 0.7)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move