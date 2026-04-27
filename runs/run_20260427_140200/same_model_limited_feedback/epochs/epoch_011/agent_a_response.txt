def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    best = None
    best_cost = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_pos = (nx, ny)
        opp_pos = (ox, oy)

        if resources:
            best_adv = None
            best_my_d = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                my_d = dist(my_pos, (rx, ry))
                op_d = dist(opp_pos, (rx, ry))
                adv = op_d - my_d
                if (best_adv is None or adv > best_adv or (adv == best_adv and my_d < best_my_d)):
                    best_adv = adv
                    best_my_d = my_d
            if best_adv is None:
                my_d_for_cost = 0
                adv_for_cost = 0
            else:
                my_d_for_cost = best_my_d
                adv_for_cost = best_adv
            cost = my_d_for_cost - 0.7 * adv_for_cost
        else:
            cost = dist(my_pos, opp_pos)  # no resources: try to reduce distance to pressure

        if best_cost is None or cost < best_cost:
            best_cost = cost
            best = [dx, dy]

    return best if best is not None else [0, 0]