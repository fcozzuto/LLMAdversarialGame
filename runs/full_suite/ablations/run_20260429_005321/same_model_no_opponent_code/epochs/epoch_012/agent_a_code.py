def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If no visible resources, drift deterministically toward opponent corner.
    if not resources:
        tx, ty = (w - 1, h - 1) if (sx, sy) == (0, 0) else (0, 0)
        bestd = [0, 0]
        bestv = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): continue
            v = cheb(nx, ny, tx, ty)
            if bestv is None or v < bestv:
                bestv, bestd = v, [dx, dy]
        return bestd

    # Choose move that maximizes advantage on best resource (self closer than opponent).
    bestd = [0, 0]
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        total = -10**9
        # Small lookahead: evaluate current step only; tie-break deterministically by order.
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Higher is better: prefer resources where we are closer, and also closer in absolute terms.
            # Use ds/do with deterministic shaping; avoid division.
            advantage = (do - ds) * 100
            closeness = -ds * 3 - (abs(nx - rx) + abs(ny - ry))
            # If ds==0 (collect), heavily prioritize.
            collect_bonus = 100000 if ds == 0 else 0
            val = advantage + closeness + collect_bonus
            if val > total:
                total = val
        if bestv is None or total > bestv:
            bestv, bestd = total, [dx, dy]
    return bestd