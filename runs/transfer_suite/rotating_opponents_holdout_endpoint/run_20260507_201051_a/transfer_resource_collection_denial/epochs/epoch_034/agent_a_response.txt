def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                return (x, y)
        return None

    s = norm_pos(observation.get("self_position")) or (0, 0)
    o = norm_pos(observation.get("opponent_position")) or (w - 1, h - 1)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        c = norm_pos(p)
        if c is not None:
            obstacles.add(c)

    resources = []
    for p in observation.get("resources") or []:
        c = norm_pos(p)
        if c is not None and c not in obstacles:
            resources.append(c)
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick resource that we can secure (largest lead), else contest the best one.
    best = None
    best_key = None
    for r in resources:
        ds = man(s, r)
        do = man(o, r)
        # Prefer: maximize (do - ds) i.e., how much closer we are than opponent.
        # Tie-break: smaller ds.
        key = (do - ds, -ds)
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best
    dx = 0 if tx == s[0] else (1 if tx > s[0] else -1)
    dy = 0 if ty == s[1] else (1 if ty > s[1] else -1)

    # Choose among the best step options the one that reduces our distance most,
    # while avoiding obstacles.
    candidates = set()
    candidates.add((dx, 0))
    candidates.add((0, dy))
    candidates.add((dx, dy))
    candidates.add((0, 0))
    # Also allow slight axis alternates deterministically for local routing.
    candidates.add((dx, -dy))
    candidates.add((-dx, dy))

    best_step = (0, 0)
    best_dist = None
    for stepx, stepy in candidates:
        nx, ny = s[0] + stepx, s[1] + stepy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = man((nx, ny), best)
        if best_dist is None or d < best_dist or (d == best_dist and (stepx, stepy) < best_step):
            best_dist = d
            best_step = (stepx, stepy)

    if best_dist is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]