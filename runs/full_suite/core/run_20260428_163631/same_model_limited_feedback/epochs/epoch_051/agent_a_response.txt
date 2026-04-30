def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev

    obs_set = set((x, y) for x, y in obstacles)

    # If no resources, just head toward center to reduce clashes.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs_set:
                    continue
                v = -dist((nx, ny), (tx, ty))
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Choose a target resource by maximizing "race advantage" (opponent distance - my distance).
    best_r = None
    best_adv = -10**18
    for r in resources:
        myd = dist((sx, sy), r)
        opd = dist((ox, oy), r)
        adv = opd - myd
        if adv > best_adv:
            best_adv = adv
            best_r = r

    tx, ty = best_r
    # Greedy move toward target, but break ties by reducing opponent's closeness to that same target.
    best = [0, 0]
    best_score = -10**18
    opp_target_dist = dist((ox, oy), (tx, ty))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs_set:
                continue
            myd = dist((nx, ny), (tx, ty))
            # Prefer closer-to-target; if equal, prefer making opponent effectively "worse" (not improving them).
            score = -myd * 100 + (opp_target_dist - dist((ox, oy), (tx, ty))) * 5
            # Slight bias to avoid staying still when movement can keep distance no worse.
            if dx == 0 and dy == 0:
                score -= 1
            if score > best_score:
                best_score = score
                best = [dx, dy]
    return best if best is not None else [0, 0]