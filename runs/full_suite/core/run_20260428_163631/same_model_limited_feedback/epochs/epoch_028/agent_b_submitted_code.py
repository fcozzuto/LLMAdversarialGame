def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obs = set(obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        opp_dist = cheb(nx, ny, ox, oy)
        if resources:
            my_best = 10**9
            opp_best = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                if myd < my_best:
                    my_best = myd
                if opd > opp_best:
                    opp_best = opd
            # Prefer moving toward close resources and away from opponent
            score = (opp_best - my_best) * 3 - opp_dist * 0.8
        else:
            score = -opp_dist

        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]