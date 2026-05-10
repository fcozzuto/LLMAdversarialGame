def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da if da > db else db

    # New policy: contest resources the opponent is already closest to (interception),
    # then move to minimize our distance while keeping it contested.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            contested = od - sd  # negative => opponent closer
            # Prefer: opponent closer (contested low), then keep it close to us, then deterministic by coords
            key = (contested, sd, od, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    dx = 0 if tx == x else (1 if tx > x else -1)
    dy = 0 if ty == y else (1 if ty > y else -1)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    nx, ny = x + dx, y + dy
    if valid(nx, ny):
        return [dx, dy]

    # Obstacle handling: choose best alternative move reducing distance to target
    curd = cheb(x, y, tx, ty)
    best_move = [0, 0]
    best_move_key = None
    for adx, ady in deltas:
        nnx, nny = x + adx, y + ady
        if not valid(nnx, nny):
            continue
        nd = cheb(nnx, nny, tx, ty)
        # Prefer reducing our distance; tie-break by deterministic order
        key = (nd, -abs(adx) - abs(ady), adx, ady)
        if best_move_key is None or (key < best_move_key and (nd <= curd or best_move_key is None)):
            best_move_key = key
            best_move = [adx, ady]

    return best_move