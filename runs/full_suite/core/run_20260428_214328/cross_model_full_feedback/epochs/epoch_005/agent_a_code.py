def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(map(tuple, obs_list))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = [(dx, dy)]
        # also allow axis-only to avoid diagonal issues
        cand += [(dx, 0), (0, dy)]
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if inside(nx, ny) and (nx, ny) not in obstacles:
                return [mx, my]
        # fallback to any valid move
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if inside(nx, ny) and (nx, ny) not in obstacles:
                return [mx, my]
        return [0, 0]

    best = None
    best_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources that we can reach first; otherwise still consider closest.
        win_bonus = 6 if sd <= od else 0
        score = win_bonus - sd + 0.1 * (od - sd)
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        # No resources: move away from opponent if possible.
        best_move = [0, 0]
        best_val = -10**18
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            val = man(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = [mx, my]
        return best_move

    rx, ry = best
    # If opponent is about to reach a resource sooner, prioritize blocking that resource.
    if man(ox, oy, rx, ry) <= 1:
        return step_toward(rx, ry)

    # Otherwise choose move that minimizes distance to target and keeps away from opponent.
    best_move = [0, 0]
    best_val = -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to = man(nx, ny, rx, ry)
        d_opp = man(nx, ny, ox, oy)
        # Slight tie-breaker toward reducing opponent access to the target.
        val = -d_to + 0.2 * d_opp - 0.05 * man(ox, oy, rx, ry)
        if val > best_val:
            best_val = val
            best_move = [mx, my]
    return best_move