def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    grid_w, grid_h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    if not resources:
        return [0, 0]

    def in_bounds(px, py):
        return 0 <= px < grid_w and 0 <= py < grid_h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource: closest to us; tie-break toward minimizing opponent access.
    best = None
    best_score = None
    for rx, ry in resources:
        d_self = cheb(x, y, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        score = (d_self, -d_opp, rx, ry)
        if best is None or score < best_score:
            best = (rx, ry)
            best_score = score
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_cmp = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        # Primary: closer to target. Secondary: keep away from opponent. Tertiary: deterministic tie.
        cmp = (d_to_target, -d_to_opp, dx, dy)
        if best_cmp is None or cmp < best_cmp:
            best_cmp = cmp
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]