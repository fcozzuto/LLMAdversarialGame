def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    tx, ty = None, None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        advantage = od - sd  # positive => we are closer
        contest = cheb(ox, oy, rx, ry)
        # Prefer strong advantage, then closer, then far from opponent (less contested).
        key = (advantage, -sd, contest, -(rx + 31 * ry))
        if best_key is None or key > best_key:
            best_key = key
            tx, ty = rx, ry

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    # Precompute if resources can be collected immediately by stepping onto them.
    res_set = set(resources)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        self_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)

        immediate = 1 if (nx, ny) == (tx, ty) else 0
        # Also discourage moves that give opponent a better shot on this target next.
        # (We assume opponent will continue toward same target; relative reduction matters.)
        current_gap = opp_d - man(sx, sy, tx, ty)
        next_gap = opp_d - self_d

        # If multiple resources exist, add tiny nudge toward staying near any resource in same region.
        region_nudge = 0
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) <= 1:
                region_nudge = 1
                break

        score = (10 * immediate, next_gap - current_gap, -self_d, region_nudge, -(abs(nx - ox) + abs(ny - oy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move