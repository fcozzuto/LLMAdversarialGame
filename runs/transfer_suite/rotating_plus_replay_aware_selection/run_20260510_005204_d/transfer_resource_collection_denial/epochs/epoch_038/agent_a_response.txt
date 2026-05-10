def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # If we can collect now, do it (deterministic tie-break by best move index then coordinates)
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    best = None
    best_move = [0, 0]

    # Evaluate each move by best resource advantage reachable from the next cell.
    for i, (dxm, dym) in enumerate(moves):
        nx, ny = sx + dxm, sy + dym
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer landing on a resource, otherwise maximize opponent-minus-self distance advantage.
        local_best = None
        local_rxry = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            on_resource = 1 if (nx == rx and ny == ry) else 0
            advantage = opd - myd
            center_bias = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
            # Higher is better: collect now first, then maximize advantage, then closer, then deterministic.
            key = (on_resource, advantage, -myd, center_bias, -(rx + ry))
            if local_best is None or key > local_best:
                local_best = key
                local_rxry = (rx, ry)

        if local_best is None:
            continue

        # Secondary preference: smaller move index for determinism if equal.
        overall = (local_best, -i)
        if best is None or overall > best:
            best = overall
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]