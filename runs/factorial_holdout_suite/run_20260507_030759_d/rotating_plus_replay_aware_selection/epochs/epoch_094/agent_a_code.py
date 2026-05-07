def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        # Chebyshev distance (diagonal allowed)
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Score resources by whether we can arrive earlier than opponent.
    # Prefer guaranteed grabs (positive lead). If none, minimize our distance.
    best = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        d_self = dist((sx, sy), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        lead = d_opp - d_self
        # Tie-break: higher lead first, then smaller self distance, then lexicographic.
        key = (lead, -d_self, -(rx + 7 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best[0], best[1]
    # If already on target, step to the next best "secure" resource; otherwise move toward target.
    cur_d_self = dist((sx, sy), (tx, ty))
    if cur_d_self == 0:
        # Choose a new resource with best security from current cell.
        best2 = None
        best2_key = None
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            d_self = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            lead = d_opp - d_self
            key = (lead, -d_self, -(rx + 7 * ry))
            if best2_key is None or key > best2_key:
                best2_key = key
                best2 = (rx, ry)
        if best2 is not None:
            tx, ty = best2[0], best2[1]

    # Move: pick legal move that improves our distance to target and maximizes lead next turn.
    best_move = (0, 0)
    best_move_key = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not ok(nx, ny):
            continue
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        lead_next = d_opp - d_self
        # Also add a small incentive to increase distance from opponent globally to reduce contention.
        opp_dist_now = dist((nx, ny), (ox, oy))
        key = (lead_next, -d_self, opp_dist_now, -(mdx * mdx + mdy * mdy))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]