def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = [0, 0]
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Choose the best resource we could "claim/deny" after this move.
        # Value favors states where opponent is farther than us, with a slight center bias.
        vbest = -10**18
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            lead = do - ds  # positive means we are closer or tie-deny
            center_bias = -0.02 * ((tx - cx) * (tx - cx) + (ty - cy) * (ty - cy))
            # If we can reach quickly, prioritize even if tie; deterministic by ordering.
            reach_bonus = 0.05 * (12 - ds) if ds <= 12 else 0.0
            v = lead + center_bias + reach_bonus
            if v > vbest:
                vbest = v
        # Small preference for staying still only when equal, to reduce jitter deterministically.
        if vbest > bestv or (vbest == bestv and [dx, dy] == [0, 0] and best != [0, 0]):
            bestv = vbest
            best = [dx, dy]

    return best