def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    resources = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]
    obstacles = {(int(x), int(y)) for x, y in (observation.get("obstacles") or [])}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    if not resources:
        bestm, bestv = (0, 0), -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            v = -cheb(nx, ny, cx, cy) - 0.35 * near_obs(nx, ny)
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # Choose a target resource: prefer where we are closer than opponent, otherwise contest opponent's nearest.
    best_target, best_tscore = None, -10**18
    for rx, ry in resources:
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        tscore = (opp_d - our_d) - 0.12 * (our_d + cheb(rx, ry, cx, cy)) - 0.6 * (1 if near_obs(rx, ry) > 0 else 0)
        if tscore > best_tscore:
            best_tscore, best_target = tscore, (rx, ry)

    tr, tc = best_target
    # If we are very behind to the chosen target, switch to contest the opponent's nearest resource.
    our_to_t = cheb(sx, sy, tr, tc)
    opp_to_t = cheb(ox, oy, tr, tc)
    if opp_to_t - our_to_t > 2:
        best2, best2v = None, 10**18
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            if d < best2v:
                best2v, best2 = d, (rx, ry)
        tr, tc = best2

    bestm, bestv = (0, 0), -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        our_d = cheb(nx, ny, tr, tc)
        opp_d = cheb(ox, oy, tr, tc)
        # Move quality: get closer to target; implicitly keep advantage where possible.
        v = -our_d + 0.5 * opp_d - 0.25 * cheb(nx, ny, cx, cy) - 0.45 * near_obs(nx, ny)
        # If target is very close