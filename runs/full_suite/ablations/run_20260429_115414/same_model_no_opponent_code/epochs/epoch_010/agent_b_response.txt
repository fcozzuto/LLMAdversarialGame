def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    if (sx, sy) in obstacles:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set(resources)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    # One-step lookahead: assume opponent doesn't move; maximize our potential advantage.
    best_mv = (0, 0)
    best_sc = -10**18
    # Softly prefer moving toward any available resource while keeping away from obstacles.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate best resource from next position.
        my_best_margin = -10**18
        my_best_dist_to_res = 10**9
        for rx, ry in resources:
            d_next = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            margin = d_opp - d_next
            if margin > my_best_margin:
                my_best_margin = margin
                my_best_dist_to_res = d_next
            elif margin == my_best_margin and d_next < my_best_dist_to_res:
                my_best_dist_to_res = d_next

        # Additional tie-breakers: keep opponent farther overall and avoid being stuck.
        opp_sep = cheb(nx, ny, ox, oy)
        # Penalize stepping into dead-end by counting how many neighboring cells are free.
        free_n = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) not in obstacles:
                free_n += 1

        sc = (my_best_margin * 1000) + (opp_sep) + (free_n * 3) - (my_best_dist_to_res)
        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    # If all candidate moves invalid (shouldn't happen), stay.
    return [int(best_mv[0]), int(best_mv[1])]