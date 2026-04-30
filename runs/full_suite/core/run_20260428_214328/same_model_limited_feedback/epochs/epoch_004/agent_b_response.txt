def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev for 8-way moves

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Choose a target resource: closest to us, but avoid those opponent is clearly closer to.
    best = None
    best_key = None
    for rx, ry in resources:
        if 0 <= rx < w and 0 <= ry < h:
            d_self = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # If opponent is much closer, deprioritize to change material targeting.
            key = (d_self + (2 if d_opp < d_self else 0) + (1 if d_opp == d_self and d_self != 0 else 0),
                   d_opp - d_self,
                   (rx + ry) % 3, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
    if best is None:
        best = (sx, sy)

    tx, ty = best

    # Evaluate moves deterministically with obstacle avoidance and improved approach.
    opp_dist_now = dist((sx, sy), (ox, oy))
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_next = dist((nx, ny), (tx, ty))
        d_opp_next = dist((nx, ny), (ox, oy))
        # Score: prioritize reaching target; then avoid letting opponent get too close; slight tie-break to stable path.
        score = (d_next,
                 -(d_opp_next),
                 abs(nx - tx) + abs(ny - ty),
                 (dx == 0 and dy == 0),
                 (nx - sx) + 2 * (ny - sy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves were blocked (should be rare), stay.
    if best_score is None:
        best_move = (0, 0)

    return [int(best_move[0]), int(best_move[1])]