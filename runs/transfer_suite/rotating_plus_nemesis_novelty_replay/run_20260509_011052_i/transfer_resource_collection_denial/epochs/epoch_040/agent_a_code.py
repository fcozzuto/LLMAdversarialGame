def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Candidate deltas (deterministic order)
    deltas = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            deltas.append([dx, dy])

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        # Evaluate as: we want to be first on some resource, but also deny closish ones to opponent.
        # For each resource, compute advantage margin (op closer? positive/negative) and our progress.
        best_over = -10**18
        worst_margin = 10**18
        close_op = 10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # positive means we are closer than opponent (in Chebyshev metric)
            if margin > best_over:
                best_over = margin
            if margin < worst_margin:
                worst_margin = margin
            dco = cheb(ox, oy, rx, ry)
            if dco < close_op:
                close_op = dco

        # Primary: maximize best advantage; Secondary: avoid moves that make opponent closest too soon
        # Tertiary: maximize our overall closeness to the "best" contested resource.
        # time pressure: if few turns, prioritize being already closest to something.
        tr = int(observation.get("turns_remaining", 0) or 0)
        urgency = 1.0 if tr <= 10 else (0.6 if tr <= 25 else 0.35)

        val = 1000.0 * best_over - 40.0 * (worst_margin * -1 if worst_margin > 0 else 0.0)
        val -= (urgency * 12.0) * close_op  # denial: keep opponent's nearest option far
        # mild bias to reduce distance to closest resource (ties)
        dmin = 10**18
        for rx, ry in resources:
            dmin = min(dmin, cheb(nx, ny, rx, ry))
        val -= urgency * dmin

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]