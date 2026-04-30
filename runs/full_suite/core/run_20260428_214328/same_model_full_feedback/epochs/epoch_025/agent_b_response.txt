def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Hold position unless it improves immediate safety vs opponent (keep simple deterministic)
        best = (0, 10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dfo = cheb(nx, ny, ox, oy)
            # maximize opponent distance, then minimize self movement
            key = (dfo, -abs(dx) - abs(dy), nx, ny)
            if key > (best[0], -best[3] - best[4], best[1], best[2]):
                best = (dfo, nx, ny, abs(dx), abs(dy))
        return [0, 0] if not inb(sx, sy) else [0, 0]

    # Choose target resource that we can reach sooner than opponent; deterministic tie-breaks.
    resources = sorted(resources, key=lambda r: (r[0], r[1]))
    best_target = None
    best_score = None
    max_consider = min(6, len(resources))
    for rx, ry in resources[:max_consider]:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # score: prioritize advantage, then smaller our distance, then fixed tie-break
        adv = do - ds  # higher is better
        # If both equal, prefer closer-to-center-ish (deterministic) to reduce collisions
        center_bias = -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2)
        score = (adv, -ds, -do, center_bias, -rx, -ry)
        if best_score is None or score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target
    # From current position, pick move that best advances towards target while maintaining advantage.
    chosen = None
    chosen_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # higher (no-ns) means we keep/extend advantage; then closer to target
        key = (no - ns, -ns, abs(dx) + abs(dy), nx, ny)
        if chosen_key is None or key > chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    if chosen is None:
        return [0, 0]
    return [int(chosen[0]), int(chosen[1])]