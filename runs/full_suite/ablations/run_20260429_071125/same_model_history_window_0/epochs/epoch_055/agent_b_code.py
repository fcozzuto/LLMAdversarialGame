def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    best_res = None
    best_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        val = (opp_d - my_d) * 5 - my_d
        if val > best_val or (val == best_val and (my_d < cheb(sx, sy, best_res[0], best_res[1]) if best_res else True)) or (val == best_val and best_res and (my_d == cheb(sx, sy, best_res[0], best_res[1]) and (rx, ry) < best_res)):
            best_val = val
            best_res = (rx, ry)

    if best_res is None:
        # fallback: move to increase distance from opponent
        best_move = [0, 0]
        best_score = -10**18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
                    continue
                d_op = cheb(nx, ny, ox, oy)
                sc = d_op * 10 - (abs(dx) + abs(dy)) * 0.1
                if sc > best_score:
                    best_score = sc
                    best_move = [dx, dy]
        return best_move

    rx, ry = best_res
    my_d0 = cheb(sx, sy, rx, ry)
    opp_d0 = cheb(ox, oy, rx, ry)
    opponent_closer = opp_d0 <= my_d0

    best_move = [0, 0]
    best_score = -10**18
    # deterministic tie-break: iterate dx,dy in fixed order and update only on strict improvement
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
                continue
            my_d = cheb(nx, ny, rx, ry)
            move_cost = (abs(dx) + abs(dy)) * 0.01
            sc = -my_d - move_cost
            if opponent_closer:
                sc += cheb(nx, ny, ox, oy) * 0.5
            else:
                sc -= cheb(nx, ny, ox, oy) * 0.05
            if sc > best_score:
                best_score = sc
                best_move = [dx, dy]
    return best_move