def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    # Deny: pick resource with greatest distance advantage over opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer large (do - ds); if tied, prefer closer ds; then prefer higher y,x for determinism.
        key = (do - ds, -ds, -ry, -rx)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = (best if best is not None else ((w - 1) // 2, (h - 1) // 2))

    # Move to neighbor that minimizes distance to the chosen target; deterministic tie-break.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                candidates.append((cheb(nx, ny, tx, ty), nx, ny, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    return [int(candidates[0][3]), int(candidates[0][4])]