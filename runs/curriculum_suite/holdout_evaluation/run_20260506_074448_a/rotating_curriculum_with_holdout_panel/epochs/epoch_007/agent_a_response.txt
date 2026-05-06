def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    valid_resources = []
    for rx, ry in resources:
        if inb(rx, ry) and (rx, ry) not in obstacles:
            valid_resources.append((rx, ry))
    if not valid_resources:
        best = min(valid_moves, key=lambda m: (cheb(m[2], m[3], ox, oy), cheb(m[2], m[3], sx, sy)))
        return [best[0], best[1]]

    # Evaluate each move by how much it improves our best contested advantage.
    best_move = None
    best_key = None
    base_adv = []
    for rx, ry in valid_resources:
        base_adv.append(cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry))
    worst_for_me = min(base_adv)

    for dx, dy, nx, ny in valid_moves:
        # For this move, consider the best resource for us (max advantage) but
        # if we're behind overall, favor moves that reduce opponent's advantage.
        best_adv = None
        best_dist = None
        best_opp_to = None
        for rx, ry in valid_resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if best_adv is None or adv > best_adv:
                best_adv, best_dist, best_opp_to = adv, myd, opd
        # Interceptor nudge: when we're behind, also keep distance from opponent.
        opp_d = cheb(nx, ny, ox, oy)
        if worst_for_me < 0:
            key = (-(best_adv), best_dist, -opp_d)
        else:
            key = (-(best_adv), best_dist, opp_d)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]