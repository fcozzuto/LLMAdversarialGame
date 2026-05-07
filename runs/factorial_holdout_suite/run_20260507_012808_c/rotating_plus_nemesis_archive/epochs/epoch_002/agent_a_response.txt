def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def time(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_delta = [0, 0]
    best_score = None

    # If no resources, move to reduce distance to opponent's corner side (deny).
    if not resources:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in occ:
                continue
            t = time((nx, ny), (tx, ty))
            score = -t
            if best_score is None or score > best_score:
                best_score = score
                best_delta = [dx, dy]
        return best_delta

    # Otherwise, pick move maximizing (we arrive earlier + resource proximity), with obstacle-aware safety.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in occ:
            continue
        my_pos = (nx, ny)
        opp_pos = (ox, oy)
        my_best = None
        for rx, ry in resources:
            my_t = time(my_pos, (rx, ry))
            op_t = time(opp_pos, (rx, ry))
            # Prefer resources we can reach sooner; strongly prefer immediate captures.
            if my_t == 0:
                adv = 1000 - op_t
            else:
                adv = (op_t - my_t) * 50 - my_t * 2
            prox = -(abs(rx - nx) + abs(ry - ny))
            score = adv + prox
            if my_best is None or score > my_best:
                my_best = score
        # Mildly penalize moving away from resources to avoid dithering.
        score2 = my_best
        if best_score is None or score2 > best_score:
            best_score = score2
            best_delta = [dx, dy]

    return best_delta