def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {tuple(p) for p in obstacles}

    cand = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ad2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if not resources:
        # Go to the corner that is farther from opponent, while staying valid.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: ad2(c[0], c[1], ox, oy))
        best = [0, 0]
        bestv = -10**18
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -ad2(nx, ny, tx, ty) - ad2(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    # Greedy contest-aware: choose move that maximizes (opponent_advantage_reversal)
    best = [0, 0]
    bestv = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # For each resource, evaluate after this move.
        # Prefer resources where we are closer than opponent; tie-break by sooner self and then stronger lead.
        for rx, ry in resources:
            sd = ad2(nx, ny, rx, ry)
            od = ad2(ox, oy, rx, ry)
            lead = od - sd
            # Higher lead is better; also encourage small self distance.
            v = lead * 1000 - sd
            if v > bestv:
                bestv, best = v, [dx, dy]
    return best