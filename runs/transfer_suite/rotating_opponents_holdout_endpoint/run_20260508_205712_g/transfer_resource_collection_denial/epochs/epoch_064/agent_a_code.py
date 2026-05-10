def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    W = observation.get("grid_width", 0)
    H = observation.get("grid_height", 0)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs_set = set()
    for o in obstacles:
        try:
            x, y = o
            obs_set.add((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    if not resources:
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can reach first; then minimize our distance; then resource position.
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        ds1 = man(nx, ny, rx, ry)
        do1 = man(ox, oy, rx, ry)
        # Also avoid moves that let opponent improve their race advantage relative to us.
        score = (ds1 - do1, ds1, abs(nx - rx) + abs(ny - ry), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]