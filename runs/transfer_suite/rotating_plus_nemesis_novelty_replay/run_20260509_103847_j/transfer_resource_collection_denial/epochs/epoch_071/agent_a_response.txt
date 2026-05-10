def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = obstacles_list if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def cell_score(x, y):
        best = None
        for rx, ry in resources:
            self_d = abs(rx - x) + abs(ry - y)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # Prefer where we're closer (opp_d - self_d larger), then closer self
            key = (-(opp_d - self_d), self_d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry), self_d, opp_d)
        return best[0], best[1], best[2], best[3]

    # Choose best target from current state
    _, (tx, ty), _, _ = cell_score(sx, sy)

    # One-step lookahead: pick neighbor that maximizes our advantage toward best target
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)
        # Prefer reducing our distance to the target; also break ties by staying closer in general
        key = (self_d - 2 * (opp_d - self_d), self_d, abs(dx) + abs(dy), dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    if best_move is not None:
        return best_move[1]

    # If all moves blocked (should be rare), stay
    return [0, 0]