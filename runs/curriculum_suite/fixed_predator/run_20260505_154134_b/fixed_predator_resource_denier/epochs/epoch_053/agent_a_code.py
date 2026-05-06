def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Focus: deny opponent by heading to resources where we can "arrive" no later than them.
    best_target = None
    best_key = None  # (we_time_margin, -resources_count, tie_break)
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # We prefer resources where we are closer or at least not much farther.
        margin = do - ds  # positive => we are better
        # Add slight bias toward resources "in front" of our current direction (toward center).
        center_bias = -cheb(sx, sy, w // 2, h // 2)
        # Tie-break stable: smaller (x+y)
        key = (margin, center_bias, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        best_target = (w // 2, h // 2)

    tx, ty = best_target

    candidates = [(-1, -1), (0, -1), (1, -1),
                  (-1, 0), (0, 0), (1, 0),
                  (-1, 1), (0, 1), (1, 1)]

    # If we are trapped by local obstacles, allow staying; otherwise avoid obvious dead-ends:
    # choose move that maximizes "effective gain" to deniable target set.
    def effective_score(x, y):
        # How quickly we can reach the chosen target
        dist_to = cheb(x, y, tx, ty)
        # Denial: consider resources where opponent is otherwise closer; we reduce their chance by moving near them.
        deny = 0
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If opponent is currently closer to that resource, our move is valuable when we can close the gap.
            if do > ds:
                # stronger if we become significantly better than opponent at arrival
                deny += (do - ds) * 2 - ds * 0.1
            else:
                # small penalty for moving away from any contested resource
                deny -= max(0, ds - do) * 0.05
        # Obstacle proximity: avoid stepping next to obstacles too much (local safety)
        near_obs = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    near_obs += 1
        return (-dist_to, deny, -near_obs, x + y)

    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = effective_score(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]