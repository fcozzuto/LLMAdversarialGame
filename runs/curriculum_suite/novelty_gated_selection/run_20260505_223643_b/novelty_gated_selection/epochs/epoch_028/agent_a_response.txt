def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    # Focal tendency: push toward resources with clear distance lead, else toward nearest.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate move by best resource contest plus safety (avoid moving into opponent pressure).
        move_best = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Lead score: strong preference for winning the race to a resource.
            lead = do - ds  # positive means we are closer or equal
            # If opponent can match/beat us, still consider but with reduced weight.
            race = lead * 100
            # Encourage shorter actual distance once lead is not decisive.
            dist_term = (40 - ds) if ds <= 6 else -ds
            # Corner/edge attraction to reduce wandering near center.
            edge = (rx == 0 or rx == w - 1 or ry == 0 or ry == h - 1)
            edge_term = 6 if edge else 0
            # If opponent is very close to this resource, penalize.
            threat = -20 if do <= 2 and do <= ds else 0
            val = race + dist_term + edge_term + threat
            if val > move_best:
                move_best = val

        # Additional safety: avoid stepping adjacent to obstacle-free line where opponent can immediately steal.
        # (Lightweight: penalize if opponent is strictly closer to *some* resource than we are and we don't improve it.)
        our_best_after = move_best
        opp_best_here = -10**18
        for rx, ry in resources:
            ds0 = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            opp_best_here = max(opp_best_here, (do - ds0) * 100 - ds0)
        # If we didn't improve against the current contest, small penalty.
        improve = our_best_after - opp_best_here
        val_total = our_best_after + (6 if improve > 0 else -3 if improve < -10 else 0)

        if val_total > best_val:
            best_val = val_total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]