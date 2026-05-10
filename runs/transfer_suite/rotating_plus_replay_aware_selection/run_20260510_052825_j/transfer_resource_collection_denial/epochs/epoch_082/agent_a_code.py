def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_res = None

    if resources:
        for rx, ry in resources:
            if not legal(rx, ry):
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if best_res is None or (-(od - sd), sd, od, rx, ry) < best_res[0]:
                best_res = ((-(od - sd), sd, od, rx, ry), (rx, ry))

    if not resources or best_res is None:
        return [0, 0]

    tx, ty = best_res[1]

    # Evaluate candidate moves by progress to target and advantage over opponent.
    best_move = (None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # If we can grab something immediately, prefer that deterministically.
        imm = 0
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                imm = 1
                break
        sd = cheb(nx, ny, tx, ty)
        td = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        score_key = (-(imm), sd, od - sd, -(td - sd), nx, ny)
        # Also include a slight preference to move away from obstacles is handled by legality; deterministic tie-break below.
        if best_move[0] is None or score_key < best_move[0]:
            best_move = (score_key, [dx, dy])

    return best_move[1] if best_move[1] is not None else [0, 0]