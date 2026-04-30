def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    res = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]
    obstacles = {(int(x), int(y)) for x, y in (observation.get("obstacles") or [])}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_block(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    if not res:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        bestv = -10**18; bestm = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            # move toward center while keeping distance from opponent
            v = (1.0 / (1 + cheb(nx, ny, ox, oy))) + 0.001 * (-(abs(nx - cx) + abs(ny - cy))) - 0.2 * near_block(nx, ny)
            if v > bestv:
                bestv = v; bestm = [dx, dy]
        return bestm

    bestv = -10**18; bestm = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Evaluate this move by the best resource we could contest next.
        v_move = -10**18
        for rx, ry in res:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)

            # Our advantage: being closer than opponent
            adv = opp_d - our_d

            # Immediate capture/adjacency pressure
            capture = 3.0 if our_d == 0 else 0.0
            adjacency_contest = 0.9 if our_d <= 1 else 0.0

            # If opponent is already closer, prefer moving into their path by minimizing our distance
            # and by blocking via adjacency to the resource.
            if opp_d <= our_d:
                contest_bias = 0.6 * (1 if our_d <= 1 else 0) + 0.25 * (-our_d)
            else:
                contest_bias = 0.25 * (adv) + 0.2 * (1 if our_d <= 2 else 0)

            # Small tie-break: prefer resources that are nearer overall (avoid long detours)
            closeness = -0.05 * our_d - 0.02 * opp_d

            v = 1.2 * adv + capture + adjacency_contest + contest_bias + closeness
            if v > v_move:
                v_move = v

        v_move -= 0.15 * near_block(nx, ny)
        if v_move > bestv:
            bestv = v_move; bestm = [dx, dy]

    return bestm