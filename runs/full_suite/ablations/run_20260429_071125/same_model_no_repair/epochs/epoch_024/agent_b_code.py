def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Deterministic target choice: try to find a resource we can reach sooner than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer: positive advantage (do - ds), then overall closeness, then determinism by coordinates.
        key = (-(do - ds), ds, rx, ry)  # smaller is better due to leading minus
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def near_obstacle_pen(x, y):
        pen = 0
        if (x, y) in occ:
            return 10**6
        for dx, dy in deltas:
            ax, ay = x + dx, y + dy
            if (ax, ay) in occ:
                pen += 6 if (dx == 0 or dy == 0) else 4
        return pen

    # Score candidate moves.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in occ:
            continue

        ds = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        # Main objective: reduce distance to target and keep opponent farther.
        score = 1000
        score -= 12 * ds
        score += 4 * (do - cheb(ox, oy, tx, ty))
        score -= near_obstacle_pen(nx, ny)
        # Tie-break deterministically: prefer moves that reduce distance to target; then lexicographic delta.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (ds, do, dx, dy) < (cheb(sx + best_move[0], sy + best_move[1], tx, ty),
                                     cheb(sx + best_move[0], sy + best_move[1], ox, oy),
                                     best_move[0], best_move[1]):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]