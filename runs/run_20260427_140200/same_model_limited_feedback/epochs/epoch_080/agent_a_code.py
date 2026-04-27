def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        myd = dist2((sx, sy), (rx, ry))
        opd = dist2((ox, oy), (rx, ry))
        # Prefer resources where we are closer; tie-break deterministically by coord.
        key = (-(opd - myd), myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    # Preferred direction toward target; then alternatives that also move us closer.
    candidates.append((dx, dy))
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            if a == 0 and b == 0:
                continue
            # Only consider moves that change at least one coordinate toward the target.
            if (a != 0 and ((sx < tx and a > 0) or (sx > tx and a < 0))) or (b != 0 and ((sy < ty and b > 0) or (sy > ty and b < 0))):
                candidates.append((a, b))
    candidates.append((0, 0))

    # Deterministic ordering for same heuristic.
    def move_score(mx, my, mdx, mdy):
        nx, ny = mx + mdx, my + mdy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        if (nx, ny) in obstacles:
            return None
        return dist2((nx, ny), (tx, ty))

    bestm = None
    bestms = None
    for m in candidates:
        mdx, mdy = m
        ms = move_score(sx, sy, mdx, mdy)
        if ms is None:
            continue
        if bestms is None or ms < bestms or (ms == bestms and (mdx, mdy) < bestm):
            bestms = ms
            bestm = (mdx, mdy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]