def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue

        # Obstacle-aware positioning: avoid getting boxed in.
        adj_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                    adj_obs += 1

        # Resource contest heuristic: prefer resources where we are closer than opponent.
        target_adv = -10**18
        target_my_d = 10**9
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            adv = op_d - my_d
            if adv > target_adv or (adv == target_adv and my_d < target_my_d):
                target_adv = adv
                target_my_d = my_d

        # If no resources, drift toward opponent slightly to maintain pressure.
        if not resources:
            target_adv = -cheb(nx, ny, ox, oy)

        # Total score: maximize advantage, slightly prefer being closer to chosen target.
        sc = (target_adv * 10.0) + (-0.15 * target_my_d) - (2.0 * adj_obs)

        if sc > best_score or (sc == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = sc
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]