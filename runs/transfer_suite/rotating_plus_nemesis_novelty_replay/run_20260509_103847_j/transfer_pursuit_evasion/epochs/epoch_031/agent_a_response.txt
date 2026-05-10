def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obs_list = observation.get("obstacles") or []
    obs = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "pursuer")).lower()
    is_evader = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_cost(x, y):
        # Hard block avoided by inside(); here we add soft penalties near obstacles.
        p = 0
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d == 0:
                return 10**9
            if d == 1:
                p += 5
            elif d == 2:
                p += 2
        return p

    best = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        oc = obstacle_cost(nx, ny)

        # Encourage moving away/toward opponent, while steering clear of obstacles.
        if is_evader:
            # Maximize distance; minimize obstacle cost.
            val = (-d) * 1.0 + oc * 1.5
        else:
            # Minimize distance; minimize obstacle cost.
            val = d * 1.0 + oc * 1.5

        # Deterministic tie-breaker: prefer moves with larger "axis progress" in the chosen direction,
        # then lexical order of delta.
        if is_evader:
            prog = abs(nx - ox) + abs(ny - oy)
        else:
            prog = -(abs(nx - ox) + abs(ny - oy))
        key = (val, -prog)

        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]