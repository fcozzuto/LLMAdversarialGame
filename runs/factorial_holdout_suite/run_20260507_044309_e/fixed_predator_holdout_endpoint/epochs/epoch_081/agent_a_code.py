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
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target selection: prioritize resources likely to be reached first by us.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Higher is better: beat opponent arrival; break ties by closeness.
        key = (do - ds, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    feasible = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            feasible.append((dx, dy))

    # Choose move that most reduces our distance to target, with opponent-denial tie-break.
    cur_ds = cheb(sx, sy, tx, ty)
    cur_do = cheb(ox, oy, tx, ty)
    bestm = None
    bestmk = None
    for dx, dy in feasible:
        nx, ny = sx + dx, sy + dy
        nds = cheb(nx, ny, tx, ty)
        # If we move towards the target while also not letting the opponent get closer, prefer it.
        ndcont = cheb(ox, oy, tx, ty) - cheb(ox, oy, tx, ty)  # 0, deterministic placeholder
        key = (-abs((cur_ds - nds)), -(nds), ndcont, dx, dy)
        # Equivalent: primarily minimize nds; then prefer smaller lexicographic dx/dy for determinism.
        key = (-nds, -abs(dx), -abs(dy), dx, dy)
        if bestmk is None or key > bestmk:
            bestmk = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]