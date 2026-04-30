def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose a target resource (favor ones we're closer to than opponent)
    target = None
    best = None
    if resources:
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            metric = (ds - do) * 10 + ds  # smaller is better; strong preference for being closer
            if best is None or metric < best:
                best = metric
                target = (rx, ry)
        # If we're not closer to any, fall back to nearest resource
        min_diff = None
        for rx, ry in resources:
            diff = dist((sx, sy), (rx, ry)) - dist((ox, oy), (rx, ry))
            if min_diff is None or diff < min_diff:
                min_diff = diff
        if min_diff is not None and min_diff > 0:
            target = min(resources, key=lambda p: dist((sx, sy), tuple(p)))
    else:
        target = None

    # Evaluate moves
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if target is not None:
            val = -dist((nx, ny), target)
            # avoid giving opponent a big advantage next
            if resources:
                # nearest contested target for opponent among remaining resources
                opp_best = None
                for rx, ry in resources:
                    do = dist((nx, ny), (rx, ry))  # our next position
                    op = dist((ox, oy), (rx, ry))
                    # measure how much we might "steal" or lose; want opponent not to be far ahead
                    score = op - do
                    if opp_best is None or score < opp_best:
                        opp_best = score
                if opp_best is not None:
                    val -= 0.5 * opp_best
        # small obstacle proximity penalty
        for ax, ay in obstacles:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                val -= 0.25
        # tie-break deterministically by dir order
        if best_val is None or val > best_val or (val == best_val and (dx, dy) == best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]