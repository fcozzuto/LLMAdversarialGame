def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    seen = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                seen.add((x, y))
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def distmax(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = -10**18
    for rx, ry in resources:
        ds = distmax((sx, sy), (rx, ry))
        do = distmax((ox, oy), (rx, ry))
        # Prefer stealing/tempo: big advantage when we can arrive sooner
        # Penalize when opponent is already earlier.
        val = (do - ds) * 100 - ds
        if do <= ds:
            val -= (ds - do + 1) * 40
        if val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best
    tx = rx - sx
    ty = ry - sy
    stepx = 0 if tx == 0 else (1 if tx > 0 else -1)
    stepy = 0 if ty == 0 else (1 if ty > 0 else -1)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if abs(dx) > 0 or abs(dy) > 0 or (dx == 0 and dy == 0):
                moves.append((dx, dy))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Try direct toward target; otherwise pick best among legal neighbors.
    nx, ny = sx + stepx, sy + stepy
    if inside(nx, ny) and (nx, ny) not in obstacles:
        return [stepx, stepy]

    curd = distmax((sx, sy), (rx, ry))
    bestm = [0, 0]
    bestm_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = distmax((nx, ny), (rx, ry))
        # Greedy toward target, with extra weight to not let opponent get a faster route.
        nd_opp = distmax((ox, oy), (rx, ry))
        val = (curd - nd) * 50 - nd + (nd_opp - nd) * 2
        if val > bestm_val:
            bestm_val = val
            bestm = [dx, dy]
    return bestm