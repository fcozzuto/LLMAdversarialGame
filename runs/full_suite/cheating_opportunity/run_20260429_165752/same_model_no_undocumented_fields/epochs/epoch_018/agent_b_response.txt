def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Deterministic "patrol": keep safe distance from opponent and drift away if too close.
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = dist(nx, ny, ox, oy)
            v = d_opp - (1 if (dx == 0 and dy == 0) else 0)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Target selection: prefer resources where we are relatively closer than opponent.
    # Score resource: our_dist - 0.85*opp_dist - 0.02*resource_index_tiebreak
    # Also avoid giving the opponent an immediate win when we are behind.
    best_resource = resources[0]
    best_res_v = 10**18
    for i, (rx, ry) in enumerate(resources):
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        immediate_threat = 1 if do <= 1 and ds > do else 0
        v = (ds - 0.85 * do) + 2.5 * immediate_threat + 0.02 * i
        if v < best_res_v:
            best_res_v = v
            best_resource = (rx, ry)

    rx, ry = best_resource

    # Choose best one-step move toward the target, but penalize moving into opponent proximity.
    # Deterministic tie-break by (dx,dy).
    best_move = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_target = dist(nx, ny, rx, ry)
        d_opp = dist(nx, ny, ox, oy)
        # Encourage reducing target distance; avoid letting opponent get closer to same target.
        opp_next = dist(ox, oy, rx, ry)
        # Use current opponent-target distance only (since opponent move not predicted).
        gain = (dist(sx, sy, rx, ry) - d_target)
        v = 4.0 * gain + (0.35 * d_opp) - (0.15 * (1 if (nx, ny) == (ox, oy) else 0)) - 0.01 * opp_next
        if v > bestv or (v == bestv and (dx, dy) < best_move):
            bestv = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]