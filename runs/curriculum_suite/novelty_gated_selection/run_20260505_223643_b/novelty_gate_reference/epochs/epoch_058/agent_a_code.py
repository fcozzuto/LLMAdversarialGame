def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    bestv = -10**18

    # Choose a primary target: nearest resource, but prefer those not on opponent's immediate diagonal
    def diag_aligned(x, y):
        return 1 if (x - ox) == (y - oy) or (x - ox) == -(y - oy) else 0

    if resources:
        target = min(resources, key=lambda t: (diag_aligned(t[0], t[1]), cheb(sx, sy, t[0], t[1])))
        tx, ty = target
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break order: as listed above

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            # If invalid, engine keeps us in place; treat as same as staying
            nx, ny = sx, sy

        # Progress toward target (lower is better)
        dt = cheb(nx, ny, tx, ty)

        # Separation from opponent (higher is better)
        do = cheb(nx, ny, ox, oy)

        # Anti-diagonal behavior: penalize landing on/near opponent's diagonal line
        aligned = diag_aligned(nx, ny)
        line_pen = 0
        if aligned:
            # Stronger penalty if also close to the opponent (diagonal probe interception)
            line_pen = 4

        # Small bias to reduce oscillations: prefer moves that change position
        moved = 1 if (dx != 0 or dy != 0) else 0

        v = (-6 * dt) + (3 * do) + moved * 0.05 - line_pen
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]