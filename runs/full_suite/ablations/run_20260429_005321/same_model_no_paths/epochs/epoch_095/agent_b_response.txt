def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    ox, oy = int(op[0]), int(op[1])

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Deterministic fallback: move toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Choose resource with best advantage: (dist_opp - dist_self) maximized
    best_r = None
    best_adv = None
    best_ds = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if best_adv is None or adv > best_adv or (adv == best_adv and (best_ds is None or ds < best_ds)) or \
           (adv == best_adv and ds == best_ds and (rx, ry) < best_r):
            best_adv, best_ds, best_r = adv, ds, (rx, ry)

    tx, ty = best_r

    # Move deterministically: prefer moves that reduce distance to target
    cur_d = cheb(sx, sy, tx, ty)
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        candidates.append((nd, abs(dx) + abs(dy), dx, dy))
    # Sort by: smallest nd, then smallest step, then fixed direction order via dx,dy
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))

    # If all moves keep same distance, still pick smallest in sorted order; deterministic.
    return [int(candidates[0][2]), int(candidates[0][3])]