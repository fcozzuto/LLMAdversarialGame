def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where we have a reach advantage; otherwise chase the best steal.
            # Key: (our advantage, negative our distance, prefer reducing both distances)
            key = (do - ds, -ds, -min(do, ds), rx, ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        # Primary: reduce our distance; Secondary: increase relative advantage; Tertiary: avoid moving toward opponent.
        key = (-ds2, do2 - ds2, -(abs(nx - tx) + abs(ny - ty)), -man(nx, ny, ox, oy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]