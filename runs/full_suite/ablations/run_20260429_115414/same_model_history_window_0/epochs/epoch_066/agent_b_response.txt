def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def cheb(a,b,c,d):
        dx = a-c; dy = b-d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    best_move = (0, 0); best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # choose resource giving maximal "closeness advantage" over opponent
        cur_best_adv = -10**9
        cur_best_selfd = 10**9
        for rx, ry in resources:
            seld = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            adv = oppd - seld
            if adv > cur_best_adv or (adv == cur_best_adv and seld < cur_best_selfd):
                cur_best_adv = adv
                cur_best_selfd = seld
        # if no resources, head to center
        if not resources:
            cx, cy = w // 2, h // 2
            cur_best_adv = 0
            cur_best_selfd = cheb(nx, ny, cx, cy)
        # score: primary advantage, then self distance, then avoid getting too close behind opponent (small)
        score = cur_best_adv * 1000 - cur_best_selfd
        opp_to_self = cheb(ox, oy, nx, ny)
        score += -opp_to_self
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]