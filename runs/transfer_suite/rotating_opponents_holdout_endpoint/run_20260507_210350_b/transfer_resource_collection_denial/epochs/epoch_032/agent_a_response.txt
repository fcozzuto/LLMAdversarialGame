def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    # Choose best target: prioritize resources where we are closer (myd-opd), then absolute closeness, then tie-break by coords.
    if resources:
        best_tx, best_ty = resources[0]
        best_key = None
        for tx, ty in resources:
            myd = man(sx, sy, tx, ty)
            opd = man(ox, oy, tx, ty)
            # smaller key is better
            key = (myd - opd, myd, abs(tx - (w - 1) / 2.0) + abs(ty - (h - 1) / 2.0), tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best_tx, best_ty = tx, ty
        tx, ty = best_tx, best_ty
    else:
        tx, ty = (sx, sy)

    # Evaluate each legal next move with a strategy tuned for resource race against deniers:
    # 1) minimize distance to target, 2) maximize distance from opponent (keep them from contesting), 3) avoid obstacles by preferring safer cells.
    best_move = [0, 0]
    best_key2 = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        myd2 = man(nx, ny, tx, ty)
        opd2 = man(nx, ny, ox, oy)

        # Safety: count blocked neighboring cells (lower is better). Deterministic and cheap.
        blocked = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                axp, ayp = nx + adx, ny + ady
                if not (0 <= axp < w and 0 <= ayp < h) or (axp, ayp) in obstacles:
                    blocked += 1

        # Collect advantage if standing on a resource.
        on_res = 1 if (nx, ny) in set(resources) else 0

        # smaller key2 is better
        key2 = (myd2, -opd2, blocked, -on_res, tx == nx and ty == ny, dx, dy)
        if best_key2 is None or key2 < best_key2:
            best_key2 = key2
            best_move = [dx, dy]
    return best_move