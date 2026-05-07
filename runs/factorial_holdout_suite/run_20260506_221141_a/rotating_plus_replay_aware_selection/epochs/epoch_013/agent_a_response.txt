def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Find best "grab" advantage from this next position.
        best_adv = None
        best_my_d = None
        for rx, ry in res:
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            adv = opp_d - my_d  # positive => likely earlier
            if best_adv is None or adv > best_adv or (adv == best_adv and my_d < best_my_d):
                best_adv = adv
                best_my_d = my_d

        # If no resources, move to maximize separation from opponent (safer).
        if not res:
            sep = dist(nx, ny, ox, oy)
            score = (sep, nx, ny)
        else:
            # Primary: maximize advantage; Secondary: minimize distance to that target.
            # Tertiary: slightly maximize distance to opponent to reduce contest collisions.
            opp_sep = dist(nx, ny, ox, oy)
            score = (best_adv, -best_my_d, opp_sep, -dx, -dy)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]