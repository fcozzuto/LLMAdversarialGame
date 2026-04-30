def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    myx, myy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_val = -10**18

    for dx, dy in deltas:
        nx = myx + dx
        ny = myy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            min_d = 10**9
            target = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < min_d:
                    min_d = d
                    target = (rx, ry)
        else:
            min_d = 0
            target = None

        if target is not None:
            rx, ry = target
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d
            res_bonus = 200 if my_d == 0 else 0
            proximity = 0
            for ax, ay in obstacles:
                dd = cheb(nx, ny, ax, ay)
                if dd == 0:
                    proximity += 100
                elif dd == 1:
                    proximity += 4
                elif dd == 2:
                    proximity += 1
            val = 18 * adv + (40 // (my_d + 1)) + res_bonus - proximity
        else:
            val = -cheb(nx, ny, ox, oy) - 2 * (abs(dx) + abs(dy))

        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best