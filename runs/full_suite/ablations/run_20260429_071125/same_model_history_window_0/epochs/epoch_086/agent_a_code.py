def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        for r in resources:
            sd = cd((sx, sy), r)
            od = cd((ox, oy), r)
            # Prefer resources where we have (or can secure) an advantage; tiebreak by being closer.
            key = (-(od - sd), sd, r[0], r[1])
            if best is None or key < best[0]:
                best = (key, r)
        target = best[1]
    else:
        target = (w // 2, h // 2)

    tx, ty = target
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        sd = cd((nx, ny), target)
        od = cd((ox, oy), target)
        # Value: reduce our distance, and also avoid moves that help the opponent's proximity.
        val = (sd, -max(0, od - sd), abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    nx, ny = sx + dx, sy + dy
    if not in_bounds(nx, ny) or (nx, ny) in obstacles:
        return [0, 0]
    return [int(dx), int(dy)]