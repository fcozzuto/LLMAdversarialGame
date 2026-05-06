def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Counter sweep_rows: avoid resources near opponent's current row; win race deterministically.
    target = resources[0]
    best = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        row_away = abs(ry - oy)  # prefer far rows from opponent's likely sweep line
        score = (opd - myd) * 1000 + row_away * 10 - myd
        if score > best or (score == best and (rx, ry) < target):
            best = score
            target = (rx, ry)

    tx, ty = target
    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Choose the move that most reliably advances toward target while not stepping into obstacles.
    best_movescore = 10**18
    best_move = [0, 0]
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            movescore = 10**12
        else:
            dist = cheb(nx, ny, tx, ty)
            curd = cheb(sx, sy, tx, ty)
            movescore = dist * 100 - (curd - dist) + (1 if (nx, ny) == (ox, oy) else 0)
        if movescore < best_movescore or (movescore == best_movescore and [dx, dy] < best_move):
            best_movescore = movescore
            best_move = [dx, dy]

    return best_move