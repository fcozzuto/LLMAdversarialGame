def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def min_dist_to_resources(px, py):
        best = 10**9
        for rx, ry in resources:
            d = md(px, py, rx, ry)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_key = None
    # Bias: if opponent is closer to the "best" resource, prioritize denier behavior.
    myd_now = min_dist_to_resources(sx, sy)
    opd_now = min_dist_to_resources(ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        landed = 1 if (nx, ny) in set(map(tuple, resources)) else 0
        myd = min_dist_to_resources(nx, ny)
        opd = opd_now  # opponent position unchanged this turn

        # Key components:
        # - primary: maximize (opd - myd): who is closer to the next pickup
        # - strong reward: landing on a resource
        # - secondary: discourage drifting away from opponent when we are not dominating
        # - tertiary: slight preference for moving toward resources even if tie
        dist_opp = md(nx, ny, ox, oy)
        key = (opd - myd, landed, -dist_opp, -(myd + (myd_now - opd_now) * 0.001))

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]