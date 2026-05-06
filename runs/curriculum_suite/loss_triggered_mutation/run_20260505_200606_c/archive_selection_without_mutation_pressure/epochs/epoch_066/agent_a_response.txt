def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    # Score resources: strongly prefer ones we can reach no later than opponent,
    # then prefer largest "lead" and shorter own distance.
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive means we are earlier
        # Primary: earlier (sd<=od). Secondary: larger lead. Tertiary: smaller sd.
        key = (1 if sd > od else 0, -lead, sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    # If already on target, try to stay (or move to next best nearby) - deterministic: stay.
    if sx == tx and sy == ty:
        return [0, 0]

    # Choose move that minimizes our distance to target; if tie, discourages giving opponent closer access
    # by also considering distance difference to target after move.
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Prefer making ourselves as early as possible; if equal, prefer move that increases our lead margin.
        key = (nsd, -(nod - nsd), dx, dy)
        if best_m is None or key < best_m[0]:
            best_m = (key, (dx, dy))
    if best_m is None:
        return [0, 0]
    return [int(best_m[1][0]), int(best_m[1][1])]