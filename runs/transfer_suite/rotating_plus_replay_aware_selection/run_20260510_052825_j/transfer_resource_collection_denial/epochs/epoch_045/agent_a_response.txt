def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid_cell(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # Pick best resource for winning timing: maximize (opp_dist - self_dist)
    best = None
    for p in resources:
        rx, ry = p[0], p[1]
        if not valid_cell(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - sd
        # Prefer positive advantage (we arrive first), then closer, then prefer smaller coords deterministically
        key = (-1 if advantage > 0 else (0 if advantage == 0 else 1), -advantage, sd, ry, rx)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If we're already on target, try to keep pressure by moving to best next-step resource
    if sx == tx and sy == ty:
        # If any resource remains, step toward the closest to maintain deterministic movement
        second_best = None
        for p in resources:
            rx, ry = p[0], p[1]
            if not valid_cell(rx, ry) or (rx == sx and ry == sy):
                continue
            d = cheb(sx, sy, rx, ry)
            key = (d, ry, rx)
            if second_best is None or key < second_best[0]:
                second_best = (key, (rx, ry))
        if second_best is None:
            return [0, 0]
        tx, ty = second_best[1]

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_cell(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # tie-break: maximize our arrival advantage vs opponent after this move
        nod = cheb(ox, oy, tx, ty)
        advantage = nod - nd
        # Also slight preference to reduce distance to opponent to contest only when equivalent
        oppd = cheb(nx, ny, ox, oy)
        key = (-1 if advantage > 0 else (0 if advantage == 0 else 1), -advantage, nd, oppd, dy, dx)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    if best_move is None:
        return [0, 0]
    return best_move[1]