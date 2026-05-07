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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    turns_remaining = int(observation.get("turns_remaining") or 0)

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        if ds > turns_remaining + 2:
            continue
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive means we reach earlier (or same if 0)
        # Prioritize safe lead; if none, prioritize our fastest/closest; discourage giving opponent a lead.
        key = (1 if margin >= 1 else 0, margin, -ds, -do, -abs((rx - sx) + (ry - sy)))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        best = min(resources, key=lambda t: cheb(sx, sy, t[0], t[1]))

    tx, ty = best

    # Try the direct step first; if blocked, pick best alternative neighbor.
    def neighbors_toward():
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        yield (dx, dy)
        # Alternatives: search 8 surrounding moves deterministically.
        for ddx, ddy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            yield (ddx, ddy)
        yield (0, 0)

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in neighbors_toward():
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        # Prefer minimizing remaining distance; then reducing opponent proximity; then deterministic tie-break.
        mkey = (-ns, -no, dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]