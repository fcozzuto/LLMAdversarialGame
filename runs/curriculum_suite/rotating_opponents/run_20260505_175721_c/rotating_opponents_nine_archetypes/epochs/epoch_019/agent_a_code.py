def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax >= ay else ay

    if not resources:
        # Deterministic fallback: move toward center-ish while respecting bounds/obstacles.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, dx, dy)
            if key < best:
                best = key + (dx, dy)
        return [best[1], best[2]] if best[0] != 10**9 else [0, 0]

    # For each move, evaluate best contested resource and maximize advantage.
    best_key = None
    best_move = (0, 0)
    res_sorted = sorted(resources)  # deterministic for tie-breaking

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        # Advantage over opponent for the same resource (Chebyshev distance works well with diagonal moves).
        best_adv = -10**9
        best_r = None
        for rx, ry in res_sorted:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we get closer than opponent
            if adv > best_adv:
                best_adv = adv
                best_r = (rx, ry)
            elif adv == best_adv and best_r is not None:
                # tie: prefer smaller myd, then lexicographic resource
                myd_best = cheb(nx, ny, best_r[0], best_r[1])
                if myd < myd_best or (myd == myd_best and (rx, ry) < best_r):
                    best_r = (rx, ry)

        # Extra pressure: keep distance from opponent so they can't immediately swing onto resources.
        # Lower opponent distance is bad for us, so we prefer higher.
        opp_d_after = cheb(nx, ny, ox, oy)

        # Build deterministic key: maximize best_adv, then maximize opp_d_after, then minimize my distance to chosen resource, then move.
        rx, ry = best_r
        myd_chosen = cheb(nx, ny, rx, ry)
        key = (-best_adv, -opp_d_after, myd_chosen, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]