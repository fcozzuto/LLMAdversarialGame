def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if inb(sx + dx, sy + dy):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # No resources: head to center while staying collision-free
    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = man((nx, ny), (cx, cy))
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # If opponent is about to grab something, contest that region by racing its nearest reachable resource.
    opp_threat = None
    best_opp_d = None
    for r in resources:
        d = man((ox, oy), r)
        if d <= 1:
            if best_opp_d is None or d < best_opp_d or (d == best_opp_d and r < opp_threat):
                best_opp_d = d
                opp_threat = r

    def nearest_d(pos, bias_resource=None):
        best_d = None
        for r in resources:
            if bias_resource is not None and r != bias_resource:
                continue
            d = man(pos, r)
            if best_d is None or d < best_d or (d == best_d and r < bias_r):
                best_d = d
                bias_r = r
        if bias_resource is not None:
            return best_d
        # nearest to any resource
        for r in resources:
            d = man(pos, r)
            if best_d is None or d < best_d:
                best_d = d
        return best_d if best_d is not None else 10**9

    # Utility: maximize (opponent_nearest - our_nearest) after our move; slight pull toward nearer resources.
    opp_pos = (ox, oy)
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        self_pos = (nx, ny)

        if opp_threat is not None:
            our_d = man(self_pos, opp_threat)
            opp_d = man(opp_pos, opp_threat)
            # contest utility: prioritize not letting opponent's advantage grow
            utility = (opp_d - our_d) * 100 - our_d
        else:
            our_d = nearest_d(self_pos)
            opp_d = nearest_d(opp_pos)
            # If we're ahead, strongly prefer; if behind, still move to reduce the gap.
            gap = opp_d - our_d
            utility = gap * 50 - our_d + (0 if resources else 0)

        # Deterministic tie-breaker: smaller dx, then smaller dy
        if best_val is None or utility > best_val or (utility == best_val and (dx, dy) < best_move):
            best_val = utility
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]