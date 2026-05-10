def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = None
    # Phase 1: pick a resource we are at least as close to as the opponent.
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if ds <= do:
            key = (-(do - ds), ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
    # Phase 2: otherwise deny by targeting the resource closest to opponent.
    if best is None:
        for rx, ry in resources:
            do = man(ox, oy, rx, ry)
            ds = man(sx, sy, rx, ry)
            key = (do, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))

    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nds = man(nx, ny, tx, ty)
        ndo = man(nx, ny, ox, oy)  # secondary pressure
        # Prefer faster approach; if tie, reduce opponent proximity to target cell.
        key = (nds, ndo, abs(nx - ox) + abs(ny - oy), rx_penalty(nx, ny, tx, ty, resources) if False else 0)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]