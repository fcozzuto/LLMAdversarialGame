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

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach strictly earlier; else minimize opponent lead.
        ahead = (od - sd)
        key = (-ahead, sd, od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), sd, od)

    if best is None:
        return [0, 0]

    tx, ty = best[1]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_step = None
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        n_sd = cheb(nx, ny, tx, ty)
        # If we step onto a resource, prioritize strongly.
        on_res = (nx, ny) in set((r[0], r[1]) for r in resources)
        # If opponent is closer to the target, reduce their advantage by moving closer.
        n_od = cheb(ox, oy, tx, ty)
        key = (0 if on_res else 1, n_sd, -(n_od - n_sd), abs((ox - nx)) + abs((oy - ny)), nx, ny)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]