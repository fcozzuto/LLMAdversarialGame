def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    best_score = -10**18
    best_move = [0, 0]

    # One-step lookahead: favor moves that improve our advantage over opponent on the most "urgent" resource,
    # with a small tie-break toward reducing our own distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        score = 0
        # Evaluate each resource by (opponent lead minus our lead); higher means better contested position.
        # Use a max-like aggregation with soft weighting to keep deterministic and simple.
        local_best = -10**18
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            lead = do - ds  # positive: we're closer (good)
            urgency = 12 - min(12, ds)  # nearer resources weigh more
            # If ds==0 we should strongly pick it.
            gain = (lead * 100) + urgency * 2 - ds
            if gain > local_best:
                local_best = gain
        score = local_best

        # Small deterministic bias to avoid getting stuck oscillating: prefer moves that reduce distance to the
        # current best resource we target (by our overall advantage from current state).
        # Compute a single target resource from current positions.
        # This is kept lightweight and deterministic.
        # (Bias only if score ties close.)
        if score > best_score or (score == best_score and (dist(nx, ny, ox, oy) < dist(sx, sy, ox, oy))):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]