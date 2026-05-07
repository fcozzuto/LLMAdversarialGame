def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        ax = a - c; ax = ax if ax >= 0 else -ax
        by = b - d; by = by if by >= 0 else -by
        return ax + by

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = min(valid, key=lambda m: (md(m[2], m[3], tx, ty), valid.index(m)))
        return [best[0], best[1]]

    res = [tuple(r) for r in resources]
    opp0 = (ox, oy)

    # Score targets from a hypothetical current position after one move
    def best_target_from(px, py):
        best = None
        best_key = None
        for i, (rx, ry) in enumerate(res):
            myd = md(px, py, rx, ry)
            opd = md(opp0[0], opp0[1], rx, ry)
            # Prefer resources we can reach not later than opponent; otherwise contest deficit.
            # Small deterministic bias by index to break ties.
            can = 1 if myd <= opd else 0
            key = (-(can), -(opd - myd), myd, i)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    chosen_target = best_target_from(sx, sy)

    # If we can't beat any resource soon, switch to closest resource that still maximizes (opd - myd)
    # by checking after-move options to ensure progress.
    best_move = None
    best_key = None
    for dx, dy, nx, ny in valid:
        t = best_target_from(nx, ny)
        tx, ty = t
        myd_next = md(nx, ny, tx, ty)
        opd_next = md(ox, oy, tx, ty)
        key = (-(1 if myd_next <= opd_next else 0), -(opd_next - myd_next), myd_next, valid.index((dx, dy, nx, ny)))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]