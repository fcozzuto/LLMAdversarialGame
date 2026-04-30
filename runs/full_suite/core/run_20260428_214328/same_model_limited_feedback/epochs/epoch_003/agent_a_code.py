def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources", [])
    obstacle_list = observation.get("obstacles", [])
    obstacle_set = set((p[0], p[1]) for p in obstacle_list)
    resource_set = set((p[0], p[1]) for p in resources)

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacle_set:
            continue

        if resources:
            my_best = -10**18
            for rx, ry in resources:
                s = dist(nx, ny, rx, ry)
                o = dist(ox, oy, rx, ry)
                adv = o - s
                if (nx, ny) == (rx, ry):
                    adv += 1000000
                if adv > my_best:
                    my_best = adv
            if my_best > best_score:
                best_score = my_best
                best_move = (dx, dy)
            elif my_best == best_score and (dx, dy) < best_move:
                best_move = (dx, dy)
        else:
            s_to_o = dist(nx, ny, ox, oy)
            score = -s_to_o + (-abs(nx - sx) - abs(ny - sy)) * 0
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]