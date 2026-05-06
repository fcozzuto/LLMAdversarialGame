def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    if resources:
        best_move = None
        best_key = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d_to_nearest = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            d_from_opp = dist(nx, ny, ox, oy)
            key = (d_to_nearest, -d_from_opp, dx * dx + dy * dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = sx + (sx - ox), sy + (sy - oy)
    best_move = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        key = (dist(nx, ny, tx, ty), -dist(nx, ny, ox, oy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]