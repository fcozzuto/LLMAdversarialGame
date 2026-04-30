def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources exist, just move toward center while keeping away from opponent
    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = (0, 0, -10**9)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if dx == 0 and dy == 0:
                    pass
                if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                    sc = dist((nx, ny), (cx, cy)) * -1 + dist((nx, ny), (ox, oy)) * 1
                    if sc > best[2]:
                        best = (dx, dy, sc)
        return [best[0], best[1]]

    # Choose a resource we are relatively more able to reach than opponent
    best_target = resources[0]
    best_val = 10**9
    for r in resources:
        rv = r[0], r[1]
        ds = dist((sx, sy), rv)
        do = dist((ox, oy), rv)
        # Prioritize closer-to-us and farther-from-them
        val = ds - 0.55 * do
        if val < best_val:
            best_val = val
            best_target = rv

    tx, ty = best_target

    # Greedy one-step move: approach target but maximize separation from opponent
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                d_to_t = dist((nx, ny), (tx, ty))
                d_to_o = dist((nx, ny), (ox, oy))
                # Slightly deter staying still unless it improves safety
                stay_pen = 0.25 if (dx == 0 and dy == 0) else 0.0
                sc = -d_to_t + 0.65 * d_to_o - stay_pen
                candidates.append((sc, dx, dy, d_to_t, d_to_o))

    # If stuck (shouldn't), return stay
    if not candidates:
        return [0, 0]

    # Deterministic tie-breaks: highest score, then smaller dist to target, then larger dist to opponent, then lexicographic dx,dy
    candidates.sort(key=lambda t: (-t[0], t[3], -t[4], t[1], t[2]))
    _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]