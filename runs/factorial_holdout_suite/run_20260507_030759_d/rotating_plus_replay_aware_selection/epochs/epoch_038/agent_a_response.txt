def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose move that maximizes our "contest advantage" on the best resource.
    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Slightly discourage moving away from any resource.
        min_self = 10**9
        min_opp = 10**9
        best_net = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds < min_self:
                min_self = ds
            if do < min_opp:
                min_opp = do

            net = do - ds  # positive = we are closer
            # Prefer resources where we are at least somewhat closer; also penalize large ds.
            score = 20 * net - ds
            if score > best_net:
                best_net = score

        # Tie-break: prefer moves that reduce nearest resource distance, then reduce our distance to opponent.
        val = best_net - 0.5 * min_self - 0.01 * man(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return best_move