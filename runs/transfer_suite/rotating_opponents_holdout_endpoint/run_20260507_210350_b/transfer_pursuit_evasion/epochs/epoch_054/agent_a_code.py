def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        dist = abs(nx - ox) + abs(ny - oy)
        return dist

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sc = score_move(dx, dy)
        if best is None or sc < best_sc:
            best = [dx, dy]
            best_sc = sc

    if best is not None:
        return best

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [dx, dy]
    return [0, 0]