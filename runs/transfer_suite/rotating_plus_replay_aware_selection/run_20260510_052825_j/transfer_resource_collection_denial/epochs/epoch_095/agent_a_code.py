def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    if not resources:
        return [0, 0]

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
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
        self_best = None
        # Evaluate how much we can "steal tempo" to the best reachable resource this turn.
        for rx, ry in resources:
            if not legal(rx, ry):
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where opponent is slower; add slight preference for closer-for-us.
            val = (od - sd) * 1000 - sd
            if self_best is None or val > self_best:
                self_best = val
        if self_best is None:
            continue
        # Tie-break: prefer moves that also keep distance from opponent (reduce contesting).
        opp_pressure = cheb(nx, ny, ox, oy)
        key = (-(self_best), opp_pressure, dx, dy)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx if legal(sx + dx, sy + dy) else 0, dy if legal(sx + dx, sy + dy) else 0)

    return [int(best_move[0]), int(best_move[1])]