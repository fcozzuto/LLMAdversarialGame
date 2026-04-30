def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)
    best_targets = []
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    if resources:
        best_adv = None
        best_choice = None
        for rx, ry in resources:
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            adv = myd - opd
            if best_adv is None or adv < best_adv or (adv == best_adv and myd < dist((sx, sy), best_choice)):
                best_adv = adv
                best_choice = (rx, ry)
        target = best_choice
    else:
        target = (w // 2, h // 2)

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    # Strategic change: if opponent is closer to the chosen target, pivot to deny by chasing the closest remaining resource.
    pivot = False
    if resources:
        pivot = dist((ox, oy), target) < dist((sx, sy), target)

    if resources and pivot:
        # choose my closest resource
        target = min(resources, key=lambda p: (dist((sx, sy), p), p[0], p[1]))

    # If resources are nearly gone, bias toward nearest safe approach to opponent (deterministic pressure).
    opp_bias = 0
    if observation.get("remaining_resource_count", len(resources)) <= 2:
        opp_bias = 1

    best_score = None
    best_move = (0, 0)
    for dx, dy, nx, ny in valid_moves:
        # avoid stepping onto opponent if alternative exists
        step_penalty = -0.8 if (nx, ny) == (ox, oy) else 0.0
        myd = dist((nx, ny), target)
        opd = dist((nx, ny), (ox, oy))
        # Favor reducing distance to target, and (slightly) increase distance if already winning on target.
        cur_myd = dist((sx, sy), target)
        improve = cur_myd - myd
        score = improve * 2.0 - myd * 0.15 - opd * (0.12 - step_penalty)
        if opp_bias:
            score += (-opd) * 0.3
        # Tie-break deterministically by move preference order
        pref = (dx, dy)
        score += -0.001 * (abs(pref[0]) + abs(pref[1]))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]