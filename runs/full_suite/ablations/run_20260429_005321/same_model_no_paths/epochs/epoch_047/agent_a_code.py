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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Deny: pick a resource where opponent is closer than we are (most urgent), else grab nearest.
    best_target = None
    best_gap = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gap = do - ds  # positive means opponent closer
        if best_target is None or (gap > best_gap) or (gap == best_gap and (rx, ry) < best_target):
            best_target, best_gap = (rx, ry), gap

    # If opponent isn't actually closer to any, just use nearest to us.
    if best_gap <= 0:
        best_target = min(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))

    tx, ty = best_target

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        candidates = [(0, 0, sx, sy)]

    # Choose move that reduces our distance to target while preventing opponent from getting closer too.
    # Deterministic tie-break by (dx,dy).
    best = None
    for dx, dy, nx, ny in candidates:
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Expect opponent to try to reduce their distance, so penalize moves that widen the advantage for them.
        # Larger target-urgency when we're farther behind.
        our = cheb(sx, sy, tx, ty)
        opp = cheb(ox, oy, tx, ty)
        behind = max(0, opp - our)
        score = (ns, - (no - ns), -behind, dx, dy)
        if best is None or score < best[0]:
            best = (score, [dx, dy])

    return best[1]