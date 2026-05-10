def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_key = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy

        # Pick the best resource you could aim for after this move
        local_best = None
        local_key = None
        for rx, ry in resources:
            if not cell_ok(rx, ry):
                continue
            self_d = dist((nx, ny), (rx, ry))
            opp_d = dist((ox, oy), (rx, ry))

            # Counter "sweep_rows": de-prioritize resources on opponent's current row,
            # because they are likely to contest or sweep within that band.
            row_pen = 1 if ry == oy else 0

            # Primary: be earlier than opponent (or at least close). Secondary: smaller self_d.
            # Tie-break deterministically by coordinates.
            key = (self_d - opp_d + row_pen * 2, self_d, rx, ry)
            if local_key is None or key < local_key:
                local_key = key
                local_best = (rx, ry)

        if local_best is None:
            continue
        # Ensure the move also heads toward the chosen target (deterministic).
        rx, ry = local_best
        heading = (0 if rx == nx else (1 if rx > nx else -1), 0 if ry == ny else (1 if ry > ny else -1))
        move_key = (local_key, abs(heading[0] - dx) + abs(heading[1] - dy), dx, dy)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = [dx, dy]

    return best_move