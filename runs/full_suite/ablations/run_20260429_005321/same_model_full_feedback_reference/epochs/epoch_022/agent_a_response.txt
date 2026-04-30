def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    def legal(nx, ny): return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        # Fallback: drift toward center while staying away from opponent
        cx, cy = w // 2, h // 2
        best = (10**9, -10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            dC = md(nx, ny, cx, cy)
            dO = md(nx, ny, ox, oy)
            cand = (dC, -dO, dx, dy)
            if cand < best:
                best = cand
        return [best[2], best[3]]

    # Target selection: maximize my advantage but also reduce opponent's advantage
    best_rx, best_ry = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        # Advantage: higher when I'm closer than opponent.
        adv = opd - myd
        # Penalize long travel and resources very close to opponent (hard to secure).
        score = adv * 10 - myd - (md(ox, oy, rx, ry) // 3)
        if score > best_score:
            best_score = score
            best_rx, best_ry = rx, ry

    # Move choice: go toward target if possible; otherwise choose best safe neighbor.
    tx, ty = best_rx, best_ry
    best = (10**9, -10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dT = md(nx, ny, tx, ty)
        dO = md(nx, ny, ox, oy)
        # Prefer reducing target distance; if tie, stay farther from opponent.
        cand = (dT, -dO, dx, dy)
        if cand < best:
            best = cand
    return [best[2], best[3]]