def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick a target resource where we can beat the opponent (smaller distance advantage).
    target = None
    best_adv = -10**9
    for tx, ty in resources[:40]:
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        adv = do - ds  # positive means we're closer
        if adv > best_adv or (adv == best_adv and (tx, ty) < target):
            best_adv = adv
            target = (tx, ty)

    # If no resources, move toward center.
    if target is None:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, int(cx + 0.5), int(cy + 0.5))
            key = (d, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    tx, ty = target
    # Score moves: minimize our distance to target and maximize distance gap vs opponent.
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = dist(nx, ny, tx, ty)
        no = dist(ox, oy, tx, ty)
        # Strongly prefer immediate pickup if possible.
        pickup = 0 if (nx == tx and ny == ty) else 1
        # Also prefer increasing separation from opponent relative to target.
        key = (pickup, ns - no, ns, dx, dy, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move is not None else [0, 0]