def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_adj_pen(x, y):
        # small deterministic penalty to avoid getting "wedged" into walls/obstacles
        p = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                p += 1
        return p

    # Heuristic: chase/evade with wall/obstacle awareness; tie-break deterministically.
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    # Prefer interior cells; helps against wall-run evasion.
    best_val = None

    # When opponent is near a boundary, favor moving to reduce/maintain component along that boundary.
    opp_near_left = ox <= 1
    opp_near_right = ox >= w - 2
    opp_near_top = oy <= 1
    opp_near_bot = oy >= h - 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        pen = obstacle_adj_pen(nx, ny)

        # Component bias (helps against wall runners): align to keep/attack along the wall.
        bias = 0
        if opp_near_left or opp_near_right:
            # focus vertical component
            bias = abs(ny - oy) - abs(sy - oy)
        elif opp_near_top or opp_near_bot:
            # focus horizontal component
            bias = abs(nx - ox) - abs(sx - ox)
        else:
            # diagonal bias
            bias = (abs(nx - ox) + abs(ny - oy)) - (abs(sx - ox) + abs(sy - oy))

        # Objective depends on role.
        # Pursuer: minimize distance; Evader: maximize distance. Add small penalties and bias.
        if is_pursuer:
            val = (d, pen, bias, -nx, -ny, dx, dy)
            better = best_val is None or val < best_val
        else:
            val = (-d, pen, -bias, nx, ny, dx, dy)
            better = best_val is None or val < best_val

        if better:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]