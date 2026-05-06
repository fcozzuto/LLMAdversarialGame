def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    valids = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not blocked(nx, ny):
            valids.append((dx, dy))

    if not valids:
        return [0, 0]

    valid_targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if inb(tx, ty) and (tx, ty) not in obs:
                valid_targets.append((tx, ty))

    if valid_targets:
        def score_target(tx, ty):
            d = abs(sx - tx) + abs(sy - ty)
            return (d, tx, ty)
        best = min(valid_targets, key=score_target)
        tx, ty = best
    else:
        tx, ty = int(ox), int(oy)

    best_move = None
    best_key = None
    for dx, dy in valids:
        nx, ny = sx + dx, sy + dy
        key = (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]