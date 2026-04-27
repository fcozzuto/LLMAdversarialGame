def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Score each move by the best "resource race" it can secure next.
    # Value = (opp_dist - my_dist_next) + small closeness bonus.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        my_best = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Encourage stealing: higher when our next distance is smaller than opponent's.
            val = (opp_d - my_d) * 100 - my_d
            if val > my_best:
                my_best = val
        # Tie-break: prefer moves that reduce distance to the closest resource now (deterministic).
        now_closest = min(resources, key=lambda p: cheb(mx, my, p[0], p[1]))
        tie = cheb(nx, ny, now_closest[0], now_closest[1])
        cur_val = my_best * 10 - tie
        if cur_val > best_val:
            best_val = cur_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]