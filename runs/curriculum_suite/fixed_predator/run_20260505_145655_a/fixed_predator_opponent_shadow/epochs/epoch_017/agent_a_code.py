def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Advantage score: resources where we can arrive sooner than opponent.
        target_best = -10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer
            val = adv * 10 - sd  # strongly prefer advantage, then closeness
            if val > target_best:
                target_best = val

        # If no advantageous target, fall back to minimizing our distance to the nearest resource.
        if target_best < 0:
            nearest_sd = min(man(nx, ny, rx, ry) for rx, ry in resources)
            val2 = -nearest_sd * 2
        else:
            val2 = target_best

        # Tie-breakers: pressure to opponent and directness to nearest resource.
        opp_pressure = -man(nx, ny, ox, oy)
        if best_val is None or (val2, opp_pressure, -man(nx, ny, resources[0][0], resources[0][1]), nx, ny) > best_val:
            best_val = (val2, opp_pressure, -man(nx, ny, resources[0][0], resources[0][1]), nx, ny)
            best = (dx, dy)

    return [best[0], best[1]]