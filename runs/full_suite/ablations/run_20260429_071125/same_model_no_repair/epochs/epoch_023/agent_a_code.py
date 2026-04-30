def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    occ = {(p[0], p[1]) for p in obstacles}

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

    def near_obstacle_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in occ:
                    pen += 5 if (ax == 0 or ay == 0) else 3
        if (x, y) in occ:
            return 10**9
        return pen

    # Pick a resource to contest: closest to us; break ties by also being far from opponent (so we can claim it).
    best_r = None
    best_key = None
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (du, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Core: reduce distance to target in Chebyshev metric.
        d1 = cheb(nx, ny, tx, ty)
        d0 = cheb(sx, sy, tx, ty)
        # Secondary: keep some distance from opponent to avoid being leapfrogged.
        do = cheb(nx, ny, ox, oy)
        # Local obstacle avoidance.
        pen = near_obstacle_pen(nx, ny)
        # Small bias to keep progressing (prefer moves that reduce current target distance).
        prog_bias = -2 if d1 < d0 else 0
        score = d1 + 0.05 * (8 - do) + pen + prog_bias
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]