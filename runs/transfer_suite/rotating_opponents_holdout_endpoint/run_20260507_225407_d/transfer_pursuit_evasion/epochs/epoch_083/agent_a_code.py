def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or not inb(x, y)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    cx, cy = w / 2.0, h / 2.0

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        dist = max(abs(nx - ox), abs(ny - oy))  # Chebyshev
        center_bias = -(abs(nx - cx) + abs(ny - cy))
        key = (dist, center_bias, -abs(dx) - abs(dy))
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is not None:
        return best

    return [0, 0]