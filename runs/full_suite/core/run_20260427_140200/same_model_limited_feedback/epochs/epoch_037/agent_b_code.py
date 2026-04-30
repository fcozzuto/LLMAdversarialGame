def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    turn = observation.get("turn_index", 0)
    obs_set = set((a, b) for a, b in obstacles)

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Decide target style: odd epochs/turns try to deny what opponent is closer to.
    deny_mode = (turn % 2 == 1)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obs_set:
            score = -1e9
        else:
            # Resource component
            if resources:
                if deny_mode:
                    # Choose a resource where opponent is closer; try to reduce their advantage.
                    res_best = None
                    res_metric = 1e18
                    for rx, ry in resources:
                        d_our = dist2(nx, ny, rx, ry)
                        d_opp = dist2(ox, oy, rx, ry)
                        # Prefer reducing opponent's closeness; also prefer not too far for us.
                        metric = (d_opp - d_our) + 0.15 * d_our
                        if metric < res_metric:
                            res_metric = metric
                            res_best = (rx, ry, d_our, d_opp)
                    d_our = res_best[2]
                    d_opp = res_best[3]
                    resource_score = -0.9 * d_our + 0.6 * (d_opp - d_our)
                else:
                    # Pure chase: minimize our distance to nearest resource.
                    mind = 1e18
                    for rx, ry in resources:
                        mind = min(mind, dist2(nx, ny, rx, ry))
                    resource_score = -mind
            else:
                resource_score = 0.0

            # Obstacle avoidance (soft): penalize being adjacent to obstacles.
            adj_pen = 0
            for ax, ay in obs_set:
                if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                    if (ax, ay) != (nx, ny):
                        adj_pen += 1
            obstacle_score = -2.0 * adj_pen

            # Opponent interaction: don't allow them easy access; mild pressure if in same direction.
            opp_d = dist2(nx, ny, ox, oy)
            opp_score = -0.02 * opp_d
            # If we can move towards a point aligned with their position, slightly encourage.
            align = 0
            if abs(nx - ox) <= 2 or abs(ny - oy) <= 2:
                align = 0.3
            score = resource_score + obstacle_score + opp_score + align

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]