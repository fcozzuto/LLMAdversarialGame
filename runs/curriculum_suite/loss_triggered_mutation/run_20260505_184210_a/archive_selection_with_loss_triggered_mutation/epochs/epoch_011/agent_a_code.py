def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Guess opponent's "sweep_rows" tendency: focus on the most populated resource row.
    cnt = {}
    for rx, ry in resources:
        cnt[ry] = cnt.get(ry, 0) + 1
    best_y = None
    best_count = -1
    for ry in sorted(cnt.keys()):
        c = cnt[ry]
        if c > best_count:
            best_count = c
            best_y = ry

    # Choose a target on that row: we want to approach it, while keeping it far from opponent.
    target = None
    best_t = -10**18
    for rx, ry in resources:
        if ry != best_y:
            continue
        d_my = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        t = (d_op - d_my) * 2.0 - d_my
        if t > best_t:
            best_t = t
            target = (rx, ry)
    if target is None:
        target = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prioritize denying the row-sweep target from opponent while still closing.
        score = (opd - myd) * 80 - myd * 3 - (abs(nx - cx) + abs(ny - cy)) * 0.05
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]