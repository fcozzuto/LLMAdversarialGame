def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    if not resources:
        # go to reduce distance to opponent slightly (deterministic)
        best = (0, 0)
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            d2o = cheb(nx, ny, ox, oy)
            key = (d2o, nx, ny)
            if best_val is None or key < best_val:
                best_val = key
                best = (dx, dy)
        return [best[0], best[1]]

    # target selection: prefer resources we can reach earlier; then overall closeness
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # We want maximize (do - ds). If negative, still choose least-bad.
        advantage = do - ds
        # tie-break deterministically by coordinates
        key = (-advantage, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # Move choice: maximize our capture likelihood and minimize being blocked near obstacles
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # local obstacle proximity penalty
        pen = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                if (nx + adx, ny + ady) in occ:
                    pen += 1 if (adx == 0 or ady == 0) else 2

        # Prefer moves that improve advantage to the target; otherwise, reduce distance to target.
        adv = do2 - ds2
        score = (-adv, ds2 + pen, nx, ny)
        # smaller is better
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]