def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose the move that maximizes "advantage" over the best target resource.
    best = (-(10**18), 0, 0)
    # Advantage for cells: prefer being closer than opponent, then closer to collect soon.
    # Small tie-break biases toward sweeping direction consistency: aim to reduce y difference first.
    y_bias = 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        local_best = -(10**18)
        for i, (rx, ry) in enumerate(resources):
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # If we land on resource, huge reward, with stable preference for earlier-index.
            if nx == rx and ny == ry:
                val = 10**12 - i
            else:
                # Opponent pressure + our speed. Prefer reducing y-gap (sweep-row tendency).
                val = (od - sd) * 120 - sd - abs(ny - ry) * y_bias
            if val > local_best:
                local_best = val

        # Secondary tie-break: prefer moves that reduce our distance to the opponent (contests) and our y-gap.
        tie = -md(nx, ny, ox, oy) - abs(ny - resources[0][1]) * 0 + (-abs(ny - oy))
        cand = (local_best, tie, -(abs(dx) + abs(dy)))
        if cand > best:
            best = cand
            best_move = [dx, dy]

    return best_move if best[1] is not None else [0, 0]