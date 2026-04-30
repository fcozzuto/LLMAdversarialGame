def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if (x, y) in obstacles:
        return [0, 0]
    if (x, y) in set(resources):
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Target selection: prefer resources where we are not worse (or least worse) than opponent, then closer.
    best_r = None
    best_key = None
    if resources:
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # lead > 0 means we are closer or equal.
            lead = do - ds
            # Tie-break deterministically by position.
            key = (lead > 0, lead, -ds, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)

    # If no resources, go to center.
    if best_r is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_r

    # Move choice: maximize score for next position vs target and vs opponent contest.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        os = cheb(ox, oy, tx, ty)
        # If opponent can reach significantly earlier, try to reduce their lead.
        contest = (os - ns)
        # Also prefer moves that increase distance from opponent when target is already within reach.
        opp_dist = cheb(nx, ny, ox, oy)
        near_resource = 1 if (nx, ny) in set(resources) else 0
        val = (near_resource, contest, ns * -1, opp_dist, -abs((nx - tx)) - abs((ny - ty)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    # Fallback (shouldn't happen): stay.
    return best_move if best_val is not None else [0, 0]