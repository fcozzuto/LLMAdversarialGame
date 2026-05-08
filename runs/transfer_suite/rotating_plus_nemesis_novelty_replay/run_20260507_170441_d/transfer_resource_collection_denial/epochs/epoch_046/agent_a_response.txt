def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Target: closest to us, but prefer ones where we are relatively closer than opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        key = (my_d, op_d <= my_d, -(op_d - my_d), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    rx, ry = best_t

    # Move selection: optimize progress to target while not letting opponent progress more.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d = dist(nx, ny, rx, ry)
        # Opponent is assumed to move next in its own direction; approximate by its current distance.
        op_d = dist(ox, oy, rx, ry)
        on_resource = 1 if (nx, ny) == (rx, ry) else 0
        # Tie-break deterministically by coordinates.
        val = (-on_resource, my_d, op_d - my_d, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]