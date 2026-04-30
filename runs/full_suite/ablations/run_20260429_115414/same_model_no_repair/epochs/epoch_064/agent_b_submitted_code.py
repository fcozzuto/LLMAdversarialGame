def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None
    best_tx = None

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        chosen = None
        chosen_adv = None
        chosen_our = None
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d
            cand = (adv, -our_d, rx, ry)  # maximize adv, then minimize our_d
            if chosen is None or cand > chosen:
                chosen = cand
                chosen_adv = adv
                chosen_our = our_d
                chosen_tx = (rx, ry)

        if chosen is None:
            continue

        # Prefer moves that can secure a contested resource; slight bias to reduce our distance.
        move_score = (chosen[0], chosen[1], -abs(chosen_tx[0] - ox) - abs(chosen_tx[1] - oy), chosen_tx[2], chosen_tx[3])
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]