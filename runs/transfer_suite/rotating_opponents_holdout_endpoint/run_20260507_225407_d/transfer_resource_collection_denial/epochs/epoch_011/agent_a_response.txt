def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_dx, best_dy = 0, 0
    best_val = -10**18
    best_sd = 10**18

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh: 
            continue
        if (nx, ny) in obstacles:
            continue

        cur_best_adv = -10**18
        cur_best_sd = 10**18
        cur_best_dist = 10**18

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # higher means we are closer (or will be first)
            # Encourage taking resources that are both winnable now and not too far
            # dist2 uses manhattan for a mild secondary preference
            dist2 = abs(nx - rx) + abs(ny - ry)
            if adv > cur_best_adv or (adv == cur_best_adv and (sd < cur_best_sd or (sd == cur_best_sd and dist2 < cur_best_dist))):
                cur_best_adv, cur_best_sd, cur_best_dist = adv, sd, dist2

        # If we can't reach any resource (shouldn't happen), fall back to stay
        if cur_best_adv < -10**17:
            continue

        # Slight bias toward reducing our own distance to the current best target
        val = cur_best_adv * 100 - cur_best_sd
        if val > best_val or (val == best_val and (cur_best_sd < best_sd or (cur_best_sd == best_sd and (dx, dy) < (best_dx, best_dy)))):
            best_val, best_sd = val, cur_best_sd
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]