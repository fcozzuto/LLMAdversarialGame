def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Choose a target resource to "race": closest by our distance, break ties by opponent being far.
    if resources:
        tx, ty = resources[0]
        best = (man(sx, sy, tx, ty), -man(ox, oy, tx, ty), tx, ty)
        for rx, ry in resources[1:]:
            cand = (man(sx, sy, rx, ry), -man(ox, oy, rx, ry), rx, ry)
            if cand < best:
                best = cand
                tx, ty = rx, ry
    else:
        # No resources visible: drift toward opponent (pressure) but avoid obstacles via legal moves.
        tx, ty = ox, oy

    # Evaluate each legal move with deterministic scoring:
    # Prefer reducing our distance to target; also slightly penalize moves that let opponent get closer to that target.
    # Add a small "escape" term toward the nearest remaining resource if the target is unset/empty.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        ds = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # If we move closer, score higher; prevent opponent advantage by comparing opponent distance after their best response estimate (static estimate).
        # Static estimate: after we move, assume opponent can move one step toward target; approximate new opponent distance = max(do-1, min dist after move)
        do_next = max(do - 1, 0)
        # Encourage reducing (our - opponent) distance to target.
        rel = (ds - do_next)
        score = -10 * rel - ds

        if resources:
            # Small term: move toward the nearest resource regardless, to recover if target disappears.
            near = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < near:
                    near = d
            score -= 0.5 * near
        else:
            # Pressure term toward opponent
            score -= 0.2 * man(nx, ny, ox, oy)

        # Deterministic tie-breaker: prefer moves with smallest (dx,dy) in lexicographic order.
        tie = (score, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or tie > best_score:
            best_score = tie
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]