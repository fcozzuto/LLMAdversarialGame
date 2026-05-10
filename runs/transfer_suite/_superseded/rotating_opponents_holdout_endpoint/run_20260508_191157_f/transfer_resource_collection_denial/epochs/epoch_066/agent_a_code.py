def choose_move(observation):
    env = observation.get("environment_name", "resource_collection")
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)
    resources = observation.get("resources") or []
    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            dx = 0 if ox == sx else (1 if ox > sx else -1)
            dy = 0 if oy == sy else (1 if oy > sy else -1)
            return [dx, dy]
        corners = [[0, 0], [0, h - 1], [w - 1, 0], [w - 1, h - 1]]
        target = max(corners, key=lambda p: abs(p[0] - ox) + abs(p[1] - oy))
        dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
        dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
        return [dx, dy]
    if env != "resource_collection":
        return [0, 0]
    if not resources:
        return [0, 0]
    # Choose resource likely to be collected first (or at least contesting).
    def score_res(r):
        rx, ry = r
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # Lower is better: prioritize closer to us and farther from opponent.
        return (ds - 0.9 * do, ds, rx, ry)
    resources_sorted = sorted(resources, key=lambda r: (r[0], r[1]))
    target = min(resources_sorted, key=score_res)
    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda m: (m[0], m[1]))
    best = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        cur_d = abs(tx - sx) + abs(ty - sy)
        # Prefer moves that reduce distance; then contest factor.
        do_next = abs(tx - ox) + abs(ty - oy)
        cand = (nd, cur_d - nd, -do_next, dx, dy)
        if cand < best:
            best = cand
    return [best[3], best[4]]