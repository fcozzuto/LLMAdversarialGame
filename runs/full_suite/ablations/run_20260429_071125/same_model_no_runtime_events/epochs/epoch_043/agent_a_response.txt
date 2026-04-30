def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Targeting change: pick a resource where we have the advantage over opponent.
    # Advantage score prefers: smaller self distance, larger opponent distance.
    target = None
    best = -10**18
    for tx, ty in resources:
        ds = kdist(sx, sy, tx, ty)
        do = kdist(ox, oy, tx, ty)
        # Encourage earlier access and being less likely to lose race
        score = (do - ds) * 2.5 - ds * 0.6 + (tx + ty) * 0.02
        if score > best:
            best = score
            target = (tx, ty)

    # If no resources, head toward center while avoiding obstacles.
    if target is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        target = (tx, ty)

    tx, ty = target

    # Greedy 1-step toward target with tie-break: avoid moving into opponent's immediate vicinity.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = kdist(nx, ny, tx, ty)
        do = kdist(nx, ny, ox, oy)
        # If opponent is close, slightly prefer moves that increase our separation.
        val = -ds * 1.3 + do * 0.35
        # Small deterministic bias to keep movement stable: prefer diagonals when equal.
        if dx != 0 and dy != 0:
            val += 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]