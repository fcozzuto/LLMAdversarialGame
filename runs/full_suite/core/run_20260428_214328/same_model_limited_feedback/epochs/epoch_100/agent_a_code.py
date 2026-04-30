def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    # Distances in Chebyshev metric (diagonal allowed)
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    # Pick a target resource where we have distance advantage
    best = None
    best_util = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Utility: prefer resources we are closer to than opponent, also prefer being closer overall
        util = (do - ds) * 5 - ds
        # If opponent is very close to that resource, slightly discourage it
        if do <= 1:
            util -= 10
        if util > best_util:
            best_util = util
            best = (rx, ry)
    if best is None:
        best = (w // 2, h // 2)

    tx, ty = best
    moves = [-1, 0, 1]
    best_move = [0, 0]
    best_score = -10**9
    # Evaluate next-step moves with obstacle and boundary handling
    for dx in moves:
        for dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            dcur = dist((sx, sy), (tx, ty))
            dnext = dist((nx, ny), (tx, ty))
            # Prefer getting closer to target; also consider cutting off opponent
            opp_d_next = dist((ox, oy), (tx, ty))
            # If we would overtake opponent's distance to the target, boost
            ds_own = dnext
            do_now = opp_d_next
            takeover = (do_now - ds_own)
            score = (dcur - dnext) * 10 + takeover * 3
            # Mild preference for moving away from immediate collision cells with opponent
            if dist((nx, ny), (ox, oy)) <= 0:
                score -= 50
            if (nx, ny) == (tx, ty):
                score += 1000
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]