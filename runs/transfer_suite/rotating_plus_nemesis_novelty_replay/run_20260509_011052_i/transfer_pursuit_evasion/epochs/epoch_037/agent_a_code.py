def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = list(map(tuple, observation.get("resources") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def is_valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not is_valid(nx, ny):
            continue
        if resources:
            # Prefer moving toward the nearest resource (deterministic tie-break).
            d = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            val = (0, d, dx, dy)
        else:
            # No resources: move toward the opponent.
            d = cheb(nx, ny, ox, oy)
            val = (1, d, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]