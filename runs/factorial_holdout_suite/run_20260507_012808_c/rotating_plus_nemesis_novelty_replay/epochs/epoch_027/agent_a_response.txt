def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Evaluate using: best resource we can reach first + secondary pressure vs opponent
    opp_best_resource = None
    opp_best_d = None
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if opp_best_d is None or d < opp_best_d or (d == opp_best_d and (rx, ry) < opp_best_resource):
            opp_best_d = d
            opp_best_resource = (rx, ry)

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        # Find our closest resource
        our_best = None
        our_best_d = None
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if our_best_d is None or d < our_best_d or (d == our_best_d and (rx, ry) < our_best):
                our_best_d = d
                our_best = (rx, ry)

        # Compare against opponent distances for the same target
        rx, ry = our_best
        opp_d_to_our_best = man(ox, oy, rx, ry)

        # If we're likely to lose that target, try to reduce opponent's best target distance
        pressure = 0
        if opp_best_resource is not None:
            brx, bry = opp_best_resource
            pressure = man(ox, oy, brx, bry) - man(nx, ny, brx, bry)

        # Score: prioritize reaching first (smaller our_d vs opp_d), then overall closeness, then pressure
        # Convert to maximization: bigger is better
        first_margin = (opp_d_to_our_best - our_best_d)  # positive means we arrive sooner
        score = first_margin * 10 - our_best_d + (2 if our_best == opp_best_resource else 0) + pressure

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]