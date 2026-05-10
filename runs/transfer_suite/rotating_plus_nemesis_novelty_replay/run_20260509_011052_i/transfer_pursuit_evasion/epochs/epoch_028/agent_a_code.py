def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def kdist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best = None
    best_val = -10**18
    self_is_evader = "evader" in str(observation.get("self_role") or "").lower()
    opp_is_evader = "evader" in str(observation.get("opponent_role") or "").lower()

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        val = 0
        if res:
            val += -min(kdist((nx, ny), r) for r in res) * 10
        d_opp = kdist((nx, ny), (ox, oy))
        if self_is_evader and not opp_is_evader:
            val += d_opp * 3
        elif opp_is_evader and not self_is_evader:
            val += -d_opp * 3
        else:
            val += (-d_opp * 1) if (not res) else 0
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]