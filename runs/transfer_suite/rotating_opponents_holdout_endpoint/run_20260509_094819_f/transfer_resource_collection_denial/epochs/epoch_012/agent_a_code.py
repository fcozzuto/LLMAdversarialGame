def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = int(observation.get("turns_remaining", 0))

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick best resource by relative closeness (we prefer ones we can reach sooner).
    best = None
    best_key = None
    for r in resources:
        if not isinstance(r, (list, tuple)) or len(r) < 2:
            continue
        tx, ty = int(r[0]), int(r[1])
        if (tx, ty) in obst:
            continue
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # Prefer: we are closer; then shorter our distance; then deterministic coordinate tie-break.
        key = (ds - do, ds, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that keep us advancing toward target while improving our advantage vs opponent.
    bestm = (0, 0)
    bestmk = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # Secondary: avoid moving away from boundary if opponent is likely to contest near end.
        boundary_pen = (0.1 * (nx + ny)) if turns_remaining < 8 else 0.0
        key = (ds2 - do, ds2, abs((nx - ox)) + abs((ny - oy)), nx, ny, boundary_pen)
        if bestmk is None or key < bestmk:
            bestmk = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]