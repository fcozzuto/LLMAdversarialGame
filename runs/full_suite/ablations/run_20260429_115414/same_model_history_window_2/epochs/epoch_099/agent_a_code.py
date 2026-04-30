def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            candidates.append((dx, dy, nx, ny))

    best = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        if resources:
            md = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            md = 10**9
        no = abs(nx - ox) + abs(ny - oy)
        # prefer closer to resource, then farther from opponent, then deterministic move order
        key = (md, -no, moves.index((dx, dy)))
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    return best if best is not None else [0, 0]