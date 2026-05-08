def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def valid_resource(r):
        return isinstance(r, (list, tuple)) and len(r) >= 2 and inb(r[0], r[1])

    valid = [r for r in resources if valid_resource(r)]
    if not valid:
        return [0, 0]

    best_move = (0, 0)
    best_key = None
    # Prefer moves that maximize advantage to winning a resource this turn.
    # Tie-break: maximize my proximity; then prefer lower opponent distance; then stable order.
    for dx, dy, nx, ny in cand:
        move_best = None
        for r in valid:
            rx, ry = r[0], r[1]
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd
            # smaller myd is better; larger adv is better; smaller opd is better
            key = (adv, -myd, -opd, rx * 100 + ry)
            if move_best is None or key > move_best:
                move_best = key
        if move_best is None:
            continue
        if best_key is None or move_best > best_key:
            best_key = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]