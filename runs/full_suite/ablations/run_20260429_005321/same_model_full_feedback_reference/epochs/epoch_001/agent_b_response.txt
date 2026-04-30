def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    cur = (sx, sy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(a, b): 
        dx = a[0] - b[0]; dy = a[1] - b[1]
        return dx*dx + dy*dy

    if not resources:
        dx = 0
        dy = 0
        best = (-10**18, (dx, dy))
        for mx in (-1, 0, 1):
            for my in (-1, 0, 1):
                nx, ny = sx + mx, sy + my
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                # drift away from opponent deterministically
                sc = (dist2((nx, ny), (ox, oy)) * 10) - (nx*1 + ny*2)
                if sc > best[0]:
                    best = (sc, (mx, my))
        return best[1]

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)
    dirs = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            dirs.append((mx, my))

    best_score = -10**18
    best_move = (0, 0)
    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep us in place
        # distances to nearest resources
        mymin = 10**18
        opmin = 10**18
        for r in res_list:
            d_m = dist2((nx, ny), r)
            if d_m < mymin: mymin = d_m
            d_o = dist2((ox, oy), r)
            if d_o < opmin: opmin = d_o
        # score: prioritize grabbing, then getting closer than opponent, and moving toward shared nearest
        sc = -mymin
        if (nx, ny) in res_set:
            sc += 10**9
        sc += (opmin - mymin) * 0.5  # lead over opponent to nearest resource
        # slight bias to reduce oscillation toward advancing (toward opponent's corner)
        sc += (abs((w - 1 - nx) - (w - 1 - sx)) * -0.01) + (abs((h - 1 - ny) - (h - 1 - sy)) * -0.01)
        # tie-break deterministic
        sc += -0.000001 * (abs(nx - sx) + abs(ny - sy)) + -0.0000001 * (nx*3 + ny*5)

        if sc > best_score:
            best_score = sc
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]