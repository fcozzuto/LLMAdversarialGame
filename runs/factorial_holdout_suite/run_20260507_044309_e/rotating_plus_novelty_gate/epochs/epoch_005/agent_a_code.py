def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set()
    for p in observation.get("obstacles", []):
        obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, 0, (0, 0))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Choose the resource that gives the best "guaranteed" advantage from this move.
        chosen = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # Key: if we can arrive no later than opponent, prioritize that.
            # Otherwise, prioritize resources that delay opponent the most relative to us.
            win = 0 if ds <= do else 1
            rel = do - ds
            # Tie-break: smaller ds, then deterministic cell order preference.
            k = (win, -rel, ds, 7 * ry + rx)
            if chosen is None or k < chosen:
                chosen = k

        if chosen is None:
            continue

        # Second-level objective: maximize our relative advantage (minimize win/negative rel/etc).
        # Add slight preference for staying closer to the opponent-competitive frontier.
        overall = (chosen[0], chosen[1], chosen[2], chosen[3])
        if overall < (best[0], best[1], best[2], best[0]):
            best = (overall[0], overall[1], (dx, dy))

    # If somehow no move was valid (blocked), stay.
    return list(best[2]) if best[2] != (0, 0) else [0, 0]