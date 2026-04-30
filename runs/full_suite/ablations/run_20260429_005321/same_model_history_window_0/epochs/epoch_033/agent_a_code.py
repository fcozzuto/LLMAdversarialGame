def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obs_set = set((a, b) for a, b in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h: 
                    continue
                if (nx, ny) in obs_set:
                    continue
                v = cheb(nx, ny, ox, oy)  # drift away
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Choose resource where we have the biggest distance advantage over opponent.
    best_r = None
    best_score = -10**18
    best_ds = 10**9
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer closeness; gain if opponent is farther; also break ties toward nearer resources.
        score = (do - ds) * 100 - ds
        if score > best_score or (score == best_score and ds < best_ds):
            best_score = score
            best_ds = ds
            best_r = (rx, ry)

    rx, ry = best_r
    # Evaluate candidate moves toward target while avoiding obstacles and limiting opponent proximity.
    best_move = [0, 0]
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue
            d_to = cheb(nx, ny, rx, ry)
            d_opp = cheb(nx, ny, ox, oy)
            # If opponent is very close to our target, prioritize getting onto/near target instead of fleeing.
            target_opp_d = cheb(ox, oy, rx, ry)
            flee_weight = 2 if target_opp_d >= 2 else 0.5
            # Also lightly prefer moves that reduce distance to opponent (to contest) when close to target.
            contest_weight = 1.2 if target_opp_d <= 1 else 0.2
            v = (-d_to) * 100 + d_opp * flee_weight + (cheb(x, y, ox, oy) - cheb(nx, ny, ox, oy)) * contest_weight
            if v > best_val:
                best_val = v
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]