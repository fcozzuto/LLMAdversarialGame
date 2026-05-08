def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand_moves.append((dx, dy, nx, ny))
    if not cand_moves:
        return [0, 0]

    if not resources:
        tx, ty = 7, 7
        if sx < w // 2:
            tx = w - 1
        if sy < h // 2:
            ty = h - 1
        resources = [(tx, ty)]

    # Pick target resource we are most likely to collect before opponent.
    best_t = None
    for tx, ty in resources:
        myd = man(sx, sy, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Prefer where we are closer; if tie, prefer closer overall.
        adv = opd - myd
        key = (-adv, myd, tx, ty)
        if best_t is None or key < best_t[0]:
            best_t = (key, tx, ty)
    tx, ty = best_t[1], best_t[2]

    myd0 = man(sx, sy, tx, ty)
    opd0 = man(ox, oy, tx, ty)

    # Choose move that maximizes our "lead" after the move, while still reducing our distance.
    best = None
    for dx, dy, nx, ny in cand_moves:
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        adv = opd - myd
        # Also slight penalty if we move away from opponent-relevant race (reduce chance they grab sooner).
        d_change = myd0 - myd  # positive is good
        score = (-(adv), -d_change, myd, dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]