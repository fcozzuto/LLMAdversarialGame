def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Choose contest target if opponent is closer there; otherwise take own nearest.
    best_t = None
    best_score = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer targets where we are not too far behind opponent; tie-break by smaller (rx+ry).
        s = (do - ds, ds, rx + ry)
        if best_score is None or s > best_score:
            best_score = s
            best_t = (rx, ry)
    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_self = man(nx, ny, tx, ty)
        # Also aim to avoid letting opponent reduce their distance to the same contested target.
        d_opp_next = man(ox, oy, tx, ty)
        d_opp_now = d_opp_next
        # Since we can't predict their move, approximate with distance to them after our move.
        d_foe = man(nx, ny, ox, oy)

        # Score: maximize progress (lower d_self), slight preference for increasing foe distance.
        # Add tiny bias to break ties deterministically by move direction order.
        val = (-d_self, d_foe, -(d_opp_now), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]