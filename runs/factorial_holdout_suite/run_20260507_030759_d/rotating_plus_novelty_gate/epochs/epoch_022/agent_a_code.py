def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_resource_value(px, py):
        if not resources:
            return -10**9, None
        bestv = None
        bestp = None
        for rx, ry in resources:
            d_me = abs(rx - px) + abs(ry - py)
            d_op = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we can reach sooner, but if opponent is already ahead,
            # shift to "denial": minimize how much closer they are.
            lead = d_op - d_me
            # Small preference for closer proximity to any resource.
            closeness = -d_me
            # Deterministic tiny tiebreak
            tb = -(rx * 8 + ry)
            v = (lead * 100) + (closeness * 2) + tb
            if bestv is None or v > bestv:
                bestv, bestp = v, (rx, ry)
        return bestv, bestp

    # One-step lookahead: pick move that maximizes best resource value
    # and breaks ties by moving toward opponent-reachable hotspots.
    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        v, tgt = best_resource_value(nx, ny)
        if tgt is None:
            v = -10**9
        # Tie-break: avoid getting closer to walls/obstacles (simple safety)
        wall_pen = -min(nx, w - 1 - nx, ny, h - 1 - ny)
        # Encourage progress toward chosen target and away from opponent if possible
        prog = 0
        if tgt is not None:
            prog = -(abs(tgt[0] - nx) + abs(tgt[1] - ny)) + (abs(tgt[0] - sx) + abs(tgt[1] - sy) <= 0)
        # Additional deterministic tie: prefer diagonal/forward-ish movement by encoding
        tb = -(dx * 3 + dy)
        score = (v * 10) + wall_pen + prog + tb
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]