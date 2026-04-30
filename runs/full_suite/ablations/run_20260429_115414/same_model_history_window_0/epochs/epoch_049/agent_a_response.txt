def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]
    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, drift to improve separation and stay away from edges only when safe
    if not resources:
        best = (10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = dist((nx, ny), (ox, oy)) - 0.01 * min(nx, ny, (w-1)-nx, (h-1)-ny)
            if sc > best[0]:
                best = (sc, (dx, dy))
        return list(best[1])

    best_sc = -10**18
    best_move = (0, 0)

    # Targeting: prefer resources we can reach sooner; otherwise go for the best available while keeping distance from opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        my_d = dist((nx, ny), (sx, sy))
        opp_d0 = dist((ox, oy), (sx, sy))
        # Small bias to avoid dithering: prefer moves that slightly reduce distance from current position? (keep stable)
        stability = -0.05 * my_d

        score_to_resources = 0.0
        best_res_score = -10**9
        for rx, ry in resources:
            rd = dist((nx, ny), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # Higher score for resources closer to us than to opponent
            rel = od - rd
            # If opponent is closer, de-prioritize strongly
            cand = (3.0 * rel) - 0.7 * rd - 0.2 * abs(rx - nx) - 0.2 * abs(ry - ny)
            if cand > best_res_score:
                best_res_score = cand

        # Separation term: avoid giving opponent easy access
        sep = dist((nx, ny), (ox, oy))
        # If we move into opponent's immediate vicinity, penalize heavily
        near_opp = 1 if sep <= 1 else 0
        opp_press = -5.0 * near_opp - 0.2 * (1 if sep == 0 else 0)

        sc = best_res_score + 0.6 * sep + stability + opp_press
        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]