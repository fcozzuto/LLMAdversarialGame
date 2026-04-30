def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If no resources visible, just keep away from opponent and obstacles.
    if not resources:
        bestd = None
        best = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_o = man(ox, oy, nx, ny)
            # Prefer increasing distance, deterministic tiebreaker by dx,dy.
            val = d_o * 10 + (dx * 0.01) + (dy * 0.001)
            if val > best:
                best, bestd = val, [dx, dy]
        return bestd if bestd is not None else [0, 0]

    # Strategic shift: maximize chances to win resource races by favoring moves that
    # make our distance advantage large; also slightly avoid getting too close to opponent.
    best_move = [0, 0]
    best_val = -10**18
    # Deterministic ordering for tie-breaks
    dirs_sorted = sorted(dirs, key=lambda t: (t[0], t[1]))
    for dx, dy in dirs_sorted:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_me = 0
        d_opp = 0
        # Evaluate best "next" resource under a race metric.
        # RaceMetric = (d_opp - d_me) + small preference for closeness.
        race_best = -10**18
        for rx, ry in resources:
            dm = man(sx + dx, sy + dy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Big weight on winning the race; small weight to reduce overall travel.
            metric = (do - dm) * 10 - dm
            if metric > race_best:
                race_best = metric
        d_opp = man(ox, oy, nx, ny)

        # Extra shaping: avoid stepping into "opponent pressure" near their position.
        val = race_best + d_opp * 0.15
        # If we're already on a resource, strongly commit (highest possible).
        for rx, ry in resources:
            if nx == rx and ny == ry:
                val += 10**6

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move