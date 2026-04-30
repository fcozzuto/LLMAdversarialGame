def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Pick a target resource where we have the best relative advantage (deterministic).
    best = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (sd - od, sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # High reward for stepping onto a resource.
        step_on = 1 if any((nx, ny) == tuple(p) for p in resources) else 0
        nd = abs(tx - nx) + abs(ty - ny)

        # Slightly avoid getting too close to opponent unless we can grab immediately.
        opp_close = abs(nx - ox) + abs(ny - oy)
        # Deterministic tie-break uses nx, ny.
        val = (-step_on, nd, -opp_close, nx, ny)
        if best_move is None or val < best_move[0]:
            best_move = (val, (dx, dy))

    if best_move is None:
        return [0, 0]
    return [int(best_move[1][0]), int(best_move[1][1])]