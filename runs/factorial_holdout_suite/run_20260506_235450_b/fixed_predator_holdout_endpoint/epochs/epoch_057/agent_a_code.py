def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Resource_denier counter: contest what the opponent is likely to reach by minimizing our deficit vs them.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        deficit = sd - od  # negative => we're ahead; positive => we must contest
        key = (deficit, sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Choose a move that reduces distance to target; if blocked, pick best alternative deterministically.
    best_move = (0, 0)
    best_dist = man(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        if d < best_dist or (d == best_dist and (dx, dy) < best_move):
            best_dist = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]