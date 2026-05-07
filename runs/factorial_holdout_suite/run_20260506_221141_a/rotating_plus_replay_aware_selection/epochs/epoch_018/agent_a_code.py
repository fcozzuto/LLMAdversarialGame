def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (gw - 1) / 2.0, (gh - 1) / 2.0

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_val = -10**18

    # Favors moves that "win" more resources in a Voronoi race sense, with a small pressure to approach the opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_score = 0.0
        my_d_opp_to_best = 10**9

        for rx, ry in res:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            if myd < opd:
                my_score += 10.0 - myd
                my_d_opp_to_best = min(my_d_opp_to_best, dist(nx, ny, ox, oy))
            elif myd == opd:
                # If we tie, slightly prefer the move that makes us closer to that resource than opponent after tying isn't possible; deterministic bias by center proximity.
                center_bias = (abs((rx - cx)) + abs((ry - cy))) * 0.01
                my_score += 4.0 - myd - center_bias

        # Secondary objective: reduce distance to opponent to deny contested resources (deterministic deterrence).
        myd_opp = dist(nx, ny, ox, oy)
        my_score -= myd_opp * 0.3

        # Tertiary deterministic tie-breaker: prefer staying closer to nearest resource.
        if res:
            mind = min(dist(nx, ny, rx, ry) for rx, ry in res)
            my_score -= mind * 0.05

        if my_score > best_val:
            best_val = my_score
            best_move = [dx, dy]
    return best_move