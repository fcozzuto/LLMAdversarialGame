def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Target preference: we pick a resource where we are at least as fast; among those,
    # prefer smaller our distance, then larger opponent distance.
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (0 if ds <= do else 1, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    rx, ry = best_t

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # Score moves by: (1) our progress to target, (2) increase our lead over opponent,
    # (3) break ties by keeping distance from opponent (avoid being contest-collided).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        self_to_t = cheb(nx, ny, rx, ry)
        opp_to_t = cheb(ox, oy, rx, ry)
        self_lead_now = cheb(sx, sy, rx, ry) - cheb(nx, ny, rx, ry)  # how much we improve
        # Prefer moves that reduce our distance and/or increase (opponent - self).
        lead_gap = (cheb(ox, oy, rx, ry) - self_to_t)
        opp_dist = cheb(nx, ny, ox, oy)

        val = (self_to_t, -lead_gap, -self_lead_now, opp_dist, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]