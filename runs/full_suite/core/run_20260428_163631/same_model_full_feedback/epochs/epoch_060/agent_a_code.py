def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        # Fallback: drift toward center while avoiding obstacles
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            dist = cheb(nx, ny, cx, cy)
            score = -dist
            if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)
        return [best[1], best[2]]

    best_target = None
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer targets where we are closer than opponent; then minimize our distance
        key = (-(opd - myd), myd, tx, ty)  # larger opd-myd is better; then smaller myd
        if best_key is None or key < best_key:
            best_key = key
            best_target = (tx, ty)

    tx, ty = best_target
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        # Additional tie-breaks: stay safe from obstacles and not mirror opponent closely
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer reducing distance to target most; then prefer being farther from opponent
        score = -d_to * 1000 + d_opp
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)
    return [best[1], best[2]]