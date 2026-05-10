def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev for 8-neighbor, diagonal cost 1

    if not resources:
        return [0, 0]

    # Pick a target deterministically: first a resource we can reach strictly earlier,
    # else a resource where we can deny the most (opp far ahead).
    best = None
    for rx, ry in resources:
        d_my = dist(sx, sy, rx, ry)
        d_op = dist(ox, oy, rx, ry)
        ahead = d_my < d_op
        # Prefer earlier secure; otherwise prefer maximizing (d_op - d_my).
        key = (0 if ahead else 1, d_my if ahead else -(d_op - d_my), d_my, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), d_my, d_op)
    (_, (tx, ty), d_my, d_op) = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Score each move by resulting advantage over opponent for the chosen target.
    # Also include tiny preference for staying closer to avoid oscillation.
    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_my_new = dist(nx, ny, tx, ty)
        adv = d_op - d_my_new  # higher is better
        score = (-adv, d_my_new, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move