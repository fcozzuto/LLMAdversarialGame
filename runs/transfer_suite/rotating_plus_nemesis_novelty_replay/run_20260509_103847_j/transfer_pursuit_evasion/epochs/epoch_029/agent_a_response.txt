def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    is_evader = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def obstacle_penalty(x, y):
        # Penalize being adjacent to obstacles (soft avoidance)
        p = 0
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d == 0:
                return 10**9
            if d == 1:
                p += 3
            elif d == 2:
                p += 1
        return p

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        pen = obstacle_penalty(nx, ny)

        # One-step tie-breaker: anticipate opponent staying around best distance
        best_opp_d = None
        for odx, ody in deltas:
            tx, ty = ox + odx, oy + ody
            if not inb(tx, ty):
                continue
            td = dist2(tx, ty, nx, ny)
            if best_opp_d is None or td < best_opp_d:
                best_opp_d = td
        if best_opp_d is None:
            best_opp_d = d

        # Objective: pursuer minimize future distance; evader maximize
        if is_evader:
            val = -(d + 0.6 * best_opp_d) - 0.35 * pen + 0.02 * (dx != 0 or dy != 0)
        else:
            val = (-(d + 0.6 * best_opp_d)) - 0.35 * pen + 0.02 * (dx != 0 or dy != 0)

        if best_val is None or (val > best_val):
            best_val = val
            best_move = [dx, dy]

    return best_move