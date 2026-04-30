def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy))
    if not valid_moves:
        return [0, 0]

    if not resources:
        return [0, 0]

    # Denial-oriented targeting: prefer resources where opponent is relatively farther.
    best = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (do - ds, -ds, rx, ry)  # maximize (do-ds), then minimize ds
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    best_move = None
    best_val = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        ds = dist((nx, ny), (tx, ty))
        do = dist((nx, ny), (ox, oy))
        # If moving closer to target helps more than getting closer to opponent
        val = (-ds, do, abs(dx) + abs(dy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]