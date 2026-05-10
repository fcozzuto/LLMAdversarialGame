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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def greedy_step(ax, ay, tx, ty):
        bestx, besty, bestd = ax, ay, 10**9
        for mdx, mdy in moves:
            nx, ny = ax + mdx, ay + mdy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                bestx, besty = nx, ny
        return bestx, besty

    if not resources:
        return [0, 0]

    # Pick a resource where we are predicted to arrive no later than opponent.
    horizon = 5
    best = None
    for rx, ry in resources:
        ax, ay = sx, sy
        bx, by = ox, oy
        da = 0
        db = 0
        for _ in range(horizon):
            if (ax, ay) == (rx, ry):
                break
            ax, ay = greedy_step(ax, ay, rx, ry)
            da += 1
        for _ in range(horizon):
            if (bx, by) == (rx, ry):
                break
            bx, by = greedy_step(bx, by, rx, ry)
            db += 1
        # Prefer smaller arrival time; break ties by advantage; then deterministic by coordinates.
        key = (da - db, da, man(sx, sy, rx, ry), rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    nx, ny = greedy_step(sx, sy, tx, ty)
    dx, dy = nx - sx, ny - sy
    if dx < -1:
        dx = -1
    elif dx > 1:
        dx = 1
    if dy < -1:
        dy = -1
    elif dy > 1:
        dy = 1
    return [int(dx), int(dy)]