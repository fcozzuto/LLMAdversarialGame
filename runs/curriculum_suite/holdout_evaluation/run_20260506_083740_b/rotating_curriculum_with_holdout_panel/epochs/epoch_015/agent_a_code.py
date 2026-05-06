def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def score_cell(x, y):
        if not valid(x, y):
            return -10**9
        # Prefer being closer to resources and also to deny opponent access.
        best = -10**9
        for rx, ry in resources:
            ds = abs(rx - x) + abs(ry - y)
            do = abs(rx - ox) + abs(ry - oy)
            # If we can get there sooner (or equal), prioritize strongly.
            rel = do - ds
            # Slight preference for central-ish squares for routing.
            center = - (abs((w - 1) / 2 - x) + abs((h - 1) / 2 - y))
            # If resource is on edge, slightly lower value (harder to contest).
            edge = (rx in (0, w - 1) or ry in (0, h - 1))
            edge_pen = -0.6 if edge else 0.0
            val = rel * 10 + center * 0.5 + edge_pen - ds * 0.2
            if val > best:
                best = val
        # If no resources, just keep distance from opponent while avoiding edges.
        if not resources:
            d_opp = abs(x - ox) + abs(y - oy)
            edge_pen = 1 if (x in (0, w - 1) or y in (0, h - 1)) else 0
            best = d_opp * 2 - edge_pen * 0.5
        return best

    if not resources:
        # Defensive: move to maximize distance from opponent while remaining safe.
        best_move = [0, 0]
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = score_cell(nx, ny)
            if v > best_val:
                best_val = v
                best_move = [dx, dy]
        return best_move

    # Targeting: evaluate next-step options toward a resource where we are currently advantaged.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = score_cell(nx, ny)
        # Mild tie-break: reduce steps to nearest resource from the candidate square.
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move