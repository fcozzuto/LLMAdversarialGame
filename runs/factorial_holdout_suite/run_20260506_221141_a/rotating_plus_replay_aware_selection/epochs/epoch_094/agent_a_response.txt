def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target_for(sx1, sy1):
        best = None
        best_val = -10**18
        for (rx, ry) in resources:
            ds = cheb(sx1, sy1, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; small preference for closer overall
            v = (do - ds) * 1000 - ds
            if v > best_val:
                best_val = v
                best = (rx, ry)
        return best

    target = best_target_for(sx, sy) if resources else None

    # If no resources visible, drift toward the farthest corner from opponent side to avoid fights
    if not target:
        tx = gw - 1 if ox < gw // 2 else 0
        ty = gh - 1 if oy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    rx, ry = target

    # If we are blocked or arrive later than opponent for the best target, switch to the best available advantage
    if resources:
        # Evaluate moves against the target plus a fallback best target
        fallback = best_target_for(sx + 0, sy + 0)
    else:
        fallback = target

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dS = cheb(nx, ny, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        score = (dO - dS) * 1000 - dS
        # Slightly bias moving toward target
        score += -cheb(nx, ny, rx, ry) * 0.01
        # If opponent is adjacent to target and we can steal it sooner, boost
        if dO == 1 and dS == 0:
            score += 5000
        # Deterministic tie-break: lexicographic by dx,dy after score
        candidates.append((score, dx, dy))

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]