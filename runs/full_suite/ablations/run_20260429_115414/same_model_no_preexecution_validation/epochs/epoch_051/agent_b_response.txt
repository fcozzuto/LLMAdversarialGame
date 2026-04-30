def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = [0, 0]
    best_score = -10**18
    target_cache = {}
    # Choose a candidate target deterministically each turn: max (opp_adv - our_adv) over resources.
    # This changes targeting materially when trailing.
    for tx, ty in resources:
        if (tx, ty) in target_cache:
            continue
        ds0 = cheb(sx, sy, tx, ty)
        do0 = cheb(ox, oy, tx, ty)
        # prioritize resources where opponent is closer or we can swing the race
        center = -(((tx - (w - 1) / 2.0) ** 2) + ((ty - (h - 1) / 2.0) ** 2))
        score = (ds0 - do0) * -1 + center * 0.01
        target_cache[(tx, ty)] = score
    # pick top 3 targets by score (deterministic via sorting)
    top_targets = sorted(resources, key=lambda p: (-target_cache[p], p[0], p[1]))[:3]

    # Evaluate each move by "first to capture" race for the most contested target among top_targets.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_score = 0.0
        for tx, ty in top_targets:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # If we get strictly closer than opponent, we gain; if not, we might deny.
            race = (do - ds)
            # Encourage becoming the unique nearest (tie-break favors us slightly).
            tie = 1.0 if ds == do else 0.0
            # Discourage walking into immediate opponent-threat region
            dist_to_opp = cheb(nx, ny, ox, oy)
            threat = -0.15 * (8 - dist_to_opp) if dist_to_opp < 4 else 0.0
            # Small center bias to stabilize paths
            center_bias = -(((tx - (w - 1) / 2.0) ** 2) + ((ty - (h - 1) / 2.0) ** 2)) * 0.002
            # Encourage reaching resources sooner than opponent by a margin
            soon = 0.25 * (7 - ds) - 0.12 * (7 - do)
            move_score += race * 1.0 + tie * 0.1 + threat + center_bias + soon
        # Prefer moves that reduce our distance to the current best contested target.
        (btx, bty) = top_targets[0]
        move_score += 0.05 * (cheb(sx, sy, btx, bty) - che