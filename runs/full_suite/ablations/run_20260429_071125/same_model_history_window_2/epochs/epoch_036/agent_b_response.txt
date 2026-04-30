def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target: prefer resources where we are strictly closer; otherwise contest likely best target.
    best = None
    best_score = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # If we can beat opponent, strongly prefer largest lead; else prefer where opponent is close too.
        if ds <= do - 1:
            lead = do - ds
            score = (-1000 - lead, ds, x, y)  # negative for "min"
        else:
            score = (ds + 0.5 * do, ds, x, y)
        if best is None or score < best_score:
            best, best_score = (x, y), score

    tx, ty = best

    # Greedy step toward target with deterministic obstacle avoidance.
    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    cand = []
    cand.append((dx, dy))
    # Try diagonal, then single-axis moves in deterministic order, then stay.
    cand.append((dx, 0))
    cand.append((0, dy))
    cand.append((dx, -dy))
    cand.append((-dx, dy))
    cand.append((0, 0))

    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if ok(nx, ny):
            # Ensure progress toward target lexicographically by distance.
            if (cheb(nx, ny, tx, ty) <= cheb(sx, sy, tx, ty)):
                return [mx, my]
    # Final fallback: any valid move minimizing distance.
    bestm = [0, 0]
    bestd = cheb(sx, sy, tx, ty)
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if ok(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd or (d == bestd and (mx, my) < (bestm[0], bestm[1])):
                    bestd = d
                    bestm = [mx, my]
    return bestm