def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    def score_to_target(tx, ty):
        return max(abs(tx - sx), abs(ty - sy))

    target = None
    best = None
    for rx, ry in resources:
        d = score_to_target(rx, ry)
        key = (d, rx, ry)
        if best is None or key < best:
            best = key
            target = (rx, ry)

    if target is None:
        tx, ty = (ox, oy)
        best_key = None
        best_move = None
        for dx, dy, nx, ny in legal_moves:
            d_opp = max(abs(nx - tx), abs(ny - ty))
            key = (-d_opp, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = target
    best_key = None
    best_move = None
    for dx, dy, nx, ny in legal_moves:
        d = max(abs(tx - nx), abs(ty - ny))
        key = (d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]