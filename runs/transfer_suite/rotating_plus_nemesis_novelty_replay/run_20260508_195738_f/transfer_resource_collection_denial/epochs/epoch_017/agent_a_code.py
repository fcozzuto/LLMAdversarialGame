def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, x, y):
        return abs(x - a) + abs(y - b)

    if resources:
        best = [0, 0]
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            best_here = -10**18
            for rx, ry in resources:
                rx = int(rx); ry = int(ry)
                sd = man(sx, sy, rx, ry)  # current self distance
                od = man(ox, oy, rx, ry)  # current opp distance
                nsd = man(nx, ny, rx, ry)  # after move distance
                # Prefer resources we can reach first and progress faster.
                adv = od - nsd
                val = adv * 20 - nsd
                # Extra pressure to prevent immediate steal when opponent is not behind.
                if od <= nsd:
                    val -= (nsd - od) * 5 + 5
                # Mild tie-break on smaller current distances (more immediate contest).
                val += (sd - od) * 2
                if val > best_here:
                    best_here = val
            if best_here > best_val:
                best_val = best_here
                best = [dx, dy]
        return best

    # No visible resources: head to the safer side opposite opponent, then bias toward a corner.
    tx = 0 if ox > sx else w - 1
    ty = 0 if oy > sy else h - 1
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]
    # Fallback: choose any valid move that reduces distance to (tx,ty) the most.
    best = [0, 0]
    bestd = 10**9
    for ddx, ddy in moves:
        cx, cy = sx + ddx, sy + ddy
        if not valid(cx, cy):
            continue
        d = abs(cx - tx) + abs(cy - ty)
        if d < bestd:
            bestd = d
            best = [ddx, ddy]
    return best