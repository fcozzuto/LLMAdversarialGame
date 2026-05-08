def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    tr = int(observation.get("turns_remaining", 0) or 0)
    my_turn = int(observation.get("turn_index", 0) or 0)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # One-step lookahead: for each candidate move, estimate best achievable lead
    best_move = (0, 0)
    best_val = -10**18
    best_tiebreak = (10**9, 10**9)

    # Mild pacing: slightly prefer nearer targets early; later, prefer high lead.
    phase = 0.0
    if tr > 0:
        phase = max(0.0, min(1.0, (45.0 - tr) / 45.0))  # deterministic w/ epoch-like shape

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Find best target from this new position
        local_best = -10**18
        local_target = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            margin = do - ds  # positive means we're closer
            # Can we plausibly get there before opponent/timeout? (rough deterministic cutoff)
            # Using turns_remaining and move count is noisy; keep soft with piecewise.
            reach_self = 1.0 if ds <= tr else 0.2
            reach_opp = 1.0 if do <= tr else 0.3
            # Score: prioritize guaranteed-looking lead; then closeness; deterministic tiebreak on coords
            val = margin * 10.0 + (-ds) * (0.8 + 0.6 * (1.0 - phase)) + (-rx - 0.01 * ry) * 0.0
            val = val * reach_self + (margin - 2.0) * 2.0 * (1.0 - reach_opp)
            if val > local_best or (val == local_best and (rx, ry) < local_target):
                local_best = val
                local_target = (rx, ry)

        # If all moves skipped due to obstacles/out-of-bounds, fall back to stay
        if local_target is None:
            continue

        # Additional tiebreak: prefer moving toward that local target with minimal (ds+do) asymmetry
        rx, ry = local_target
        ds2 = man(nx, ny, rx, ry)
        do2 = man(ox, oy, rx, ry)
        tieb = (-margin if (do2 - ds2) is not None else 0, ds2)
        if local_best > best_val or (local_best == best_val and tieb < best_tiebreak):
            best_val = local_best
            best_move = (dx, dy)
            best_tiebreak = tieb

    return [int(best_move[0]), int(best_move[1])]