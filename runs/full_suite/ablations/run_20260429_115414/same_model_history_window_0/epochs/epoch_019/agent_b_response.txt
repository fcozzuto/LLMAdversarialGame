def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d): return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - ds
        key = (adv, -ds, -((rx + ry) % 3))
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    steps = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (sx, sy) == (tx, ty):
        return [0, 0]

    best_move = (None, None)
    best_score = None
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = dist(nx, ny, tx, ty)
        do2 = dist(ox, oy, tx, ty)
        score = (-ds2, (do2 - ds2), (dx == 0 and dy == 0))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move[0] is None:
        return [0, 0]
    return best_move