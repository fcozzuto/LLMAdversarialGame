def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    self_name = observation.get("self_name", "self")
    opponent_name = observation.get("opponent_name", "opponent")

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # No resources: drift toward center to reduce opponent escape paths
        tx, ty = w // 2, h // 2
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            v = -(abs(nx - tx) + abs(ny - ty))
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    res_set = set(tuple(p) for p in resources)
    candidates = []
    for r in resources:
        r = tuple(r)
        # Prefer targets where we can get there sooner than opponent
        self_d = dist((sx, sy), r)
        opp_d = dist((ox, oy), r)
        candidates.append((opp_d - self_d, -self_d, r))
    candidates.sort(reverse=True)
    # Consider only top few to keep deterministic and concise
    top_targets = [t[2] for t in candidates[:3]]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        step_to_res = 1 if (nx, ny) in res_set else 0

        # Evaluate move by best advantage among top targets
        val = step_to_res * 10**6
        for r in top_targets:
            self_d2 = dist((nx, ny), r)
            opp_d2 = dist((ox, oy), r)
            # Also slightly penalize moving away from target
            val = max(val, step_to_res * 10**6 + (opp_d2 - self_d2) * 1000 - self_d2)
        # Tie-break deterministically by preferring moves that reduce distance to nearest resource
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: smallest dx then dy
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]