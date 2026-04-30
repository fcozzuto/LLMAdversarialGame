def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        # No resources: drift toward center while keeping distance from opponent
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = [0, 0]
        bestv = -10**18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    nx, ny = sx, sy
                dv = -((nx - tx) ** 2 + (ny - ty) ** 2) - 1.5 * ((nx - ox) ** 2 + (ny - oy) ** 2)
                if dv > bestv:
                    bestv = dv
                    best = [dx, dy]
        return best

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    mypos = (sx, sy)
    opppos = (ox, oy)
    # Choose a contested target: maximize (opponent distance - my distance)
    best_target = resources[0]
    best_adv = -1e18
    for r in resources:
        adv = dist(opppos, r) - dist(mypos, r)
        if adv > best_adv:
            best_adv = adv
            best_target = r

    tx, ty = best_target[0], best_target[1]

    # Evaluate candidate moves with a compact heuristic
    best_move = [0, 0]
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                nx, ny = sx, sy
                dx = 0
                dy = 0
            np = (nx, ny)
            if np in set((p[0], p[1]) for p in resources):
                val = 1000.0
            else:
                val = 0.0
            d_my = dist(np, (tx, ty))
            d_opp = dist(opppos, np)
            # Progress to target + deny opponent proximity
            val += 40.0 / (1.0 + d_my) - 0.9 * d_opp
            # Secondary: avoid moving into being the closest to opponent's nearest resource
            # (soft blocking by not letting them gain easy captures)
            nearest_r_to_opp = None
            best_do = 1e18
            for r in resources:
                do = dist(opppos, r)
                if do < best_do:
                    best_do = do
                    nearest_r_to_opp = r
            d_opp_to_target_r = dist(opppos, nearest_r_to_opp)
            d_my_to_same_r = dist(np, nearest_r_to_opp)
            val += 6.0 * (d_opp_to_target_r - d_my_to_same_r)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    return best_move