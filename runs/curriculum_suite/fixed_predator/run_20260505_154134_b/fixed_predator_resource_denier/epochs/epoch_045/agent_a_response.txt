def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obs

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
                  (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_target = None
    best_val = None

    # Choose a target that we can reach earlier than the opponent (deterministic bias to deny).
    alpha = 0.65
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Larger means better for us.
        val = (do - ds) - alpha * ds + 0.01 * (rx + ry)
        if best_val is None or val > best_val:
            best_val = val
            best_target = (rx, ry)

    if best_target is None:
        # Conservative center drift.
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_target

    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        dist_to = cheb(nx, ny, tx, ty)
        dist_opp = cheb(nx, ny, ox, oy)

        # Prefer reaching the target quickly while staying away from opponent pressure.
        # Tie-break deterministically by favoring moves that also improve "deny" potential.
        deny = (cheb(ox, oy, tx, ty) - dist_to)
        score = (-dist_to, dist_opp, -deny, nx + 3 * ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]