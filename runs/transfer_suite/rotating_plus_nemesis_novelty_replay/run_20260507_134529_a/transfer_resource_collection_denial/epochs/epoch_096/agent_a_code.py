def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = [0, 0]
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = man(nx, ny, ox, oy)
            if bestv is None or v < bestv or (v == bestv and (nx, ny) < (sx + best[0], sy + best[1])):
                bestv = v
                best = [dx, dy]
        return best

    # If on a resource, keep still to collect.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # Choose a target resource: maximize (opp_dist - self_dist), then prefer nearer.
    # If opponent is much closer, heavily penalize that resource.
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        penalty = 0
        if lead < 0:
            penalty = 10 * (-lead)  # avoid resources where opponent is closer
        # Small tie-break towards higher x then y for determinism
        key = (lead - penalty, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    # Move one step toward target, but never step into obstacles/bounds; include local safety via opponent distance.
    best = [0, 0]
    best_tuple = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = man(nx, ny, rx, ry)
        d_opp = man(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: keep farther from opponent to reduce contention.
        tup = (-(d_to_t), d_opp, -dx, -dy, (nx, ny))
        if best_tuple is None or tup > best_tuple:
            best_tuple = tup
            best = [dx, dy]
    return [int(best[0]), int(best[1])]