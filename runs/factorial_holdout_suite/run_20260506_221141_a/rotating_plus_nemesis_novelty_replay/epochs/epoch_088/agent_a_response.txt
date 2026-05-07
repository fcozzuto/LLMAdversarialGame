def choose_move(observation):
    def get_xy(key):
        p = observation.get(key, (0, 0))
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        return 0, 0

    sx, sy = get_xy("self_position")
    ox, oy = get_xy("opponent_position")
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Score targets by our lead (opponent_dist - our_dist) then by our distance.
    # Prefer deterministic ordering by coordinates.
    best = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        lead = do - ds
        # If we can't lead, still take the target with the best lead (least negative),
        # but break ties by smaller ds and then lexicographic coords.
        key = (-lead, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    dx = tx - sx
    dy = ty - sy
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

    # Deterministically avoid stepping into obstacles if possible.
    candidates = []
    for sxm, sym in [(step_x, step_y), (step_x, 0), (0, step_y), (step_x, -step_y), (0, 0)]:
        nx, ny = sx + sxm, sy + sym
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
            candidates.append((sxm, sym))
    if not candidates:
        candidates = [(0, 0)]

    # Choose the candidate that reduces our manhattan distance the most; tie-break by parity.
    curd = manh(sx, sy, tx, ty)
    bestm = None
    for xm, ym in candidates:
        nd = manh(sx + xm, sy + ym, tx, ty)
        k = (-(curd - nd), xm * 2 + ym, sxm := xm, sym := ym)
        if bestm is None or k < bestm[0]:
            bestm = (k, [int(xm), int(ym)])
    return bestm[1]