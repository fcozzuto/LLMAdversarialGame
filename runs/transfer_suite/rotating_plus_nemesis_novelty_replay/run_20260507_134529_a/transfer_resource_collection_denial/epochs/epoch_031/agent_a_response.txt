def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]
    # One-step lookahead: choose move that maximizes the best contest advantage over remaining resources.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        # obstacle proximity penalty to reduce bumping loops
        prox = 0
        for ax, ay in obstacles:
            dd = cheb(nx, ny, ax, ay)
            if dd <= 1:
                prox += 2
            elif dd == 2:
                prox += 1
        # evaluate resources: take the best "net" advantage this move can secure now
        best_net = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            net = (op_d - my_d) * 10 - my_d
            # if we can reach immediately but opponent is far, prioritize
            if my_d == 0 and op_d > 0:
                net += 200
            # if we're clearly behind, heavily discount
            if my_d > op_d:
                net -= (my_d - op_d) * 30
            if net > best_net:
                best_net = net
        val = best_net - prox
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]