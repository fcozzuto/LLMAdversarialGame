def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate by best resource after this move.
        move_best = -10**18
        for i, (rx, ry) in enumerate(resources):
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)

            if nx == rx and ny == ry:
                val = 10**12 - i  # immediate pickup
            else:
                # Main contest: prefer being closer/sooner than opponent.
                # Add slight penalty for far distance to keep paths efficient.
                val = (do - ds) * 1000 - ds
                # Mild bias toward resources that are "closer on our route"
                # (breaks ties in a consistent way).
                val += (md(sx, sy, rx, ry) - md(ox, oy, rx, ry)) * 3

            # Deterministic tie-break by resource index then by score.
            if val > move_best:
                move_best = val

        if best_score is None or move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]