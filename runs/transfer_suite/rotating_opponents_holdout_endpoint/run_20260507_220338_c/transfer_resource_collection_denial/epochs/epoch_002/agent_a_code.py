def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((x, y) for x, y in obstacles_list)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Choose move that best contests resources: minimize (our_distance - opp_distance),
        # then our distance as a secondary factor.
        move_best = None
        move_best_adv = None
        for rx, ry in resources:
            sdist = manhattan(nx, ny, rx, ry)
            odist = manhattan(ox, oy, rx, ry)
            # Strongly prefer resources we can be closer to than the opponent.
            val = (sdist - odist) * 1000 + sdist
            adv = odist - sdist  # positive means we are closer
            if move_best is None or val < move_best or (val == move_best and adv > move_best_adv):
                move_best = val
                move_best_adv = adv

        # Slight preference for moves that reduce distance to the opponent (shadow-like pressure)
        # to prevent being "chased off" contested spots.
        opp_bias = manhattan(nx, ny, ox, oy) * 1
        total = move_best + opp_bias * (-1 if move_best_adv and move_best_adv > 0 else 1)

        if best_val is None or total < best_val:
            best_val = total
            best_move = (dx if (sx + dx, sy + dy) != (sx, sy) or (sx + dx, sy + dy) in obstacles else 0, dy if (sx + dx, sy + dy) != (sx, sy) or (sx + dx, sy + dy) in obstacles else 0)
            # Actually, if move was invalid, nx,ny==sx,sy; then dx,dy should be [0,0].
            if (sx + dx, sy + dy) in obstacles or not in_bounds(sx + dx, sy + dy):
                best_move = (0, 0)

    return [best_move[0], best_move[1]]