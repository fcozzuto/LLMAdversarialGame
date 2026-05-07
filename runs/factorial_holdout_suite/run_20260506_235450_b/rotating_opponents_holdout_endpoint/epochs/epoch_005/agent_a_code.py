def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_key = None

    # If no resources, drift toward opponent (deterministic fallback)
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    # One-step lookahead: pick next cell that maximizes how much closer we are than opponent
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy  # engine would keep us in place on invalid moves
        # Score best resource for us this turn
        best_gain = None
        best_self = None
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            gain = od - sd  # positive means we are closer than opponent
            if best_gain is None or (gain, -sd) > (best_gain, best_self):
                best_gain = gain
                best_self = -sd
        # Also slightly prefer reducing our distance to the currently closest opponent-tempting resource
        # (opponent archetype: nearest_resource)
        opp_closest = None
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            od = manh(ox, oy, rx, ry)
            if opp_closest is None or od < opp_closest[0]:
                opp_closest = (od, rx, ry)
        opp_sd = manh(nx, ny, opp_closest[1], opp_closest[2]) if opp_closest else 10**9

        key = (best_gain, -opp_sd, -(abs(nx - sx) + abs(ny - sy)), -manh(nx, ny, sx, sy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx if inb(sx + dx, sy + dy) else 0, dy if inb(sx + dx, sy + dy) else 0]  # dx/dy still in {-1,0,1}

    # Ensure dx,dy are valid
    return [best_move[0] if best_move[0] in (-1, 0, 1) else 0, best_move[1] if best_move[1] in (-1, 0, 1) else 0]