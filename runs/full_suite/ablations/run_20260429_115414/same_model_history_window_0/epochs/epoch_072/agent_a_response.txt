def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Select a target resource that we can reach sooner than the opponent.
    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gap = od - sd  # positive means we are closer (or equal)
        # Prefer winning race; then prefer shorter distance.
        key = (gap, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        # No resources known: move to reduce distance to opponent while avoiding obstacles
        target = (ox, oy)
    else:
        target = best

    tx, ty = target
    # Evaluate moves deterministically.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist_self(x, y):
        return cheb(x, y, tx, ty)
    def dist_opp(x, y):
        return cheb(x, y, ox, oy)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = dist_self(nx, ny)
        # Prefer moves that get closer to target, keep distance from opponent, and avoid stepping into obstacle is handled.
        # Also add a small deterministic tie-break toward staying within bounds center-ish.
        do = dist_opp(nx, ny)
        key = (-ds, -do, dx, dy)  # minimize ds, maximize do
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    # If all moves blocked, stay.
    dx, dy = best_move
    return [int(dx), int(dy)]