def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Sort resources: prioritize those opponent can reach relatively soon.
    resources_sorted = sorted(resources, key=lambda r: (man(ox, oy, r[0], r[1]), r[0], r[1]))
    k = 5 if len(resources_sorted) >= 5 else len(resources_sorted)
    contested = resources_sorted[:k]

    # Precompute obstacle adjacency for a mild repulsion.
    def obstacle_pen(nx, ny):
        p = 0
        for ex, ey in obstacles:
            d = abs(nx - ex) + abs(ny - ey)
            if d == 1:
                p += 2
            elif d == 0:
                p += 100
        return p

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue

        # Interception/value heuristic:
        # If we are closer than opponent to some resource, reward it strongly.
        # If not, try to reduce the opponent's advantage; also repel from the opponent a bit.
        rel_best = -10**9
        self_min_to_cont = 10**9
        opp_min_to_cont = 10**9
        for rx, ry in contested:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds < self_min_to_cont:
                self_min_to_cont = ds
            if do < opp_min_to_cont:
                opp_min_to_cont = do
            rel = do - ds
            if rel > rel_best:
                rel_best = rel

        # Repel: don't walk into opponent while trying to contest.
        repel = man(nx, ny, ox, oy)

        # Deterministic tie-break: prefer smaller (rx,ry) implicitly via keys.
        key = (
            -rel_best,                        # maximize rel_best
            self_min_to_cont,                # then closer to some contested resource
            -repel,                           # then farther from opponent
            obstacle_pen(nx, ny),            # then safer from obstacles
            dx, dy
        )

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]