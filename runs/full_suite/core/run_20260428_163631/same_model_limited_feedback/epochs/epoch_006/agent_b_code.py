def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        return [0, 0]

    def clamp(x, a, b):
        return a if x < a else (b if x > b else x)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_resource_target():
        best = None
        best_val = -10**18
        for r in resources:
            md = dist((sx, sy), r)
            od = dist((ox, oy), r)
            val = (od - md) * 10 - md
            if r == (sx, sy):
                val += 10**6
            if val > best_val:
                best_val = val
                best = r
        return best

    target = best_resource_target()

    opp_first_bias = 0
    if resources:
        # If opponent is clearly closer to the current target, switch to one it can't reach first.
        md_t = dist((sx, sy), target)
        od_t = dist((ox, oy), target)
        if od_t <= md_t:
            for r in resources:
                md = dist((sx, sy), r)
                od = dist((ox, oy), r)
                if (od - md) > opp_first_bias:
                    opp_first_bias = (od - md)
                    target = r

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        my_d = dist((nx, ny), target)
        opp_d = dist((ox, oy), target)
        # Prefer being closer to a target where we can arrive before opponent.
        firstness = (opp_d - my_d)
        score = firstness * 20 - my_d - (dx == 0 and dy == 0) * 1.0
        # Avoid getting too close to opponent (prevents herding into losing races).
        score -= max(0, 6 - dist((nx, ny), (ox, oy))) * 0.6
        # Opportunistically move onto any resource.
        if (nx, ny) in set(resources):
            score += 10**5
        # Small obstacle proximity penalty (discourage corridors that can trap you).
        for ax, ay in obstacles:
            if abs(nx - ax) <= 1 and abs(ny - ay) <= 1:
                score -= 0.25
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]