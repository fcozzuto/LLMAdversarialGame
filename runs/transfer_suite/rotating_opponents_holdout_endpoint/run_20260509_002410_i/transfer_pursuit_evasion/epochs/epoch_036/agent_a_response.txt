def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def manh(a, b, c, d):
        t = a - c
        if t < 0:
            t = -t
        u = b - d
        if u < 0:
            u = -u
        return t + u

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer moving toward the farthest corner from the opponent, but always maximize separation.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Deterministic corner choice: pick max manhattan; tie-break by fixed order.
    target = corners[0]
    best_corner_d = -10**9
    for c in corners:
        d = manh(c[0], c[1], ox, oy)
        if d > best_corner_d:
            best_corner_d = d
            target = c

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    # Deterministic tie-break order: slight bias away from staying still if equal.
    moves.sort(key=lambda m: (m == (0, 0), m[0], m[1]))

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist_op = manh(nx, ny, ox, oy)

        # Obstacle pressure: reward moves that keep distance from obstacles.
        min_obs = 10**9
        if obstacles:
            for ex, ey in obstacles:
                dd = manh(nx, ny, ex, ey)
                if dd < min_obs:
                    min_obs = dd

        dist_corner = manh(nx, ny, target[0], target[1])
        # We want to increase distance from opponent first; second, drift toward far corner.
        # Penalize getting too close to any obstacle.
        score = dist_op * 1000 + dist_corner * 5 + (min_obs if min_obs != 10**9 else 0) * 3

        # If we can directly increase corner distance from opponent significantly, prefer it.
        score += (dist_op >= manh(sx, sy, ox, oy)) * 20

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]