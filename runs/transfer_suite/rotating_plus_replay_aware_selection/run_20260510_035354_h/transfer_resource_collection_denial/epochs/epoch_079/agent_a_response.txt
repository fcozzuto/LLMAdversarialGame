def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    # Target selection: race for resource; also avoid opponent row/column when close.
    best = None
    best_key = None
    for rx, ry in res:
        sd = cd(sx, sy, rx, ry)
        od = cd(ox, oy, rx, ry)
        avoid = 0
        if sd <= 2 and ry == oy:
            avoid = 3
        if sd <= 2 and rx == ox:
            avoid = 2
        key = (od - sd - avoid, -sd, -abs(ry - oy), -abs(rx - ox), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    # Deterministic tie-break: favor smallest self distance, then best race advantage, then fixed order.
    best_mv = None
    best_key = None
    for dx, dy, nx, ny in moves:
        sd = cd(nx, ny, tx, ty)
        od = cd(ox, oy, tx, ty)  # opponent fixed this turn
        rowcol_push = 0
        if ry == oy and sd <= 1:
            rowcol_push = -2
        key = ( -sd, (od - sd) + rowcol_push, -nx, -ny, dx, dy )
        if best_key is None or key > best_key:
            best_key = key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]