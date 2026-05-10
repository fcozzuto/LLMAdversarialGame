def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obst

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def best_next(ax, ay, tx, ty):
        best = (ax, ay)
        bestd = 10**9
        for mdx, mdy in moves:
            nx, ny = ax + mdx, ay + mdy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (nx, ny)
        return best

    if not resources:
        return [0, 0]

    # Choose contested resource where we are predicted to arrive no later than opponent.
    horizon = 6
    best_key = None
    best_target = resources[0]
    for rx, ry in resources:
        ax, ay = sx, sy
        bx, by = ox, oy
        da = None
        db = None
        for t in range(horizon + 1):
            if da is None and ax == rx and ay == ry:
                da = t
            if db is None and bx == rx and by == ry:
                db = t
            if da is not None and db is not None:
                break
            if t < horizon:
                if ax != rx or ay != ry:
                    ax, ay = best_next(ax, ay, rx, ry)
                if bx != rx or by != ry:
                    bx, by = best_next(bx, by, rx, ry)
        if da is None:
            da = horizon + 1
        if db is None:
            db = horizon + 1

        # Prefer us arriving earlier; tie-break toward earlier self arrival and then closer overall.
        key = (db - da, -da, -(abs(rx - sx) + abs(ry - sy)))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    nx, ny = best_next(sx, sy, tx, ty)
    dx = nx - sx
    dy = ny - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [dx, dy]