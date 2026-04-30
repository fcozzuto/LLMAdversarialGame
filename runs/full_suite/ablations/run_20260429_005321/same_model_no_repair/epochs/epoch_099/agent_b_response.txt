def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    adj8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def risk(x, y):
        r = 0
        if (x, y) in obst:
            return 10**6
        for dx, dy in adj8:
            if (x + dx, y + dy) in obst:
                r += 3
        return r

    if not resources:
        # deterministic drift toward opponent while avoiding obstacles
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, ox, oy)
            v = -d - risk(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        # Evaluate move by best "race" resource we can reach sooner than opponent
        move_best = -10**18
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if our_d == 0:
                race = 10**6
            else:
                race = (opp_d - our_d) * 12
            # tie-breaks: slightly prefer nearer resources and more central paths
            center_bias = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.01
            score = race - our_d - 0.15 * risk(nx, ny) + center_bias
            if score > move_best:
                move_best = score
        # Also avoid moving into high-risk cells even if race looks good
        move_val = move_best - 0.6 * risk(nx, ny)
        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]