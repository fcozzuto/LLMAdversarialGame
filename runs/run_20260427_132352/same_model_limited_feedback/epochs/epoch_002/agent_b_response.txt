def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    best = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer resources we are at least as close to; otherwise still take if none.
        take = (sd <= od)
        key = (0 if take else 1, sd, -(od - sd), rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    (rx, ry) = best[1]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-break: prefer smaller resulting distance; then prefer closer to target on x then y; then by move order
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (rx, ry))
        key = (nd, abs(rx - nx) + abs(ry - ny), nx, ny, moves.index((dx, dy)))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]