def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Choose target: prefer resources where we are closer and/or opponent is far; slightly bias toward
    # targets on our "side" (based on start corners) to change strategy from pure advantage-greedy.
    if resources:
        side = 1 if sx <= w // 2 else -1  # if on left half, prefer smaller x targets; else larger x
        best = None
        best_key = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # main: maximize (do - ds), then minimize ds, then prefer targets more on our side, then deterministic tie-break
            side_bias = (tx - (w // 2)) * side
            key = (-(do - ds), ds, -side_bias, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
    else:
        # If no visible resources: move to a corner that is opposite the opponent's horizontal bias,
        # aiming to control space for future resource visibility.
        left_corner = (0, 7) if oy < h // 2 else (0, 0)
        right_corner = (w - 1, 0) if oy < h // 2 else (w - 1, h - 1)
        tx, ty = left_corner if ox > w // 2 else right_corner

    # Pick move: minimize our distance to target while also increasing opponent distance; avoid blocked.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        # maximize opponent separation and closeness to target; deterministic tie-break by move order
        key = (ds, -do, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]