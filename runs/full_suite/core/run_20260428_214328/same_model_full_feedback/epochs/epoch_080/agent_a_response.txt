def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Target: resource where we have the biggest advantage over opponent (opp farther than us)
    if resources:
        best_t = None
        best_v = -10**9
        for tx, ty in resources:
            sd = md(sx, sy, tx, ty)
            od = md(ox, oy, tx, ty)
            v = (od - sd) * 10 - sd
            # slight preference for nearer to avoid getting stuck
            if v > best_v:
                best_v = v
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        # No resources: go to a corner near our side of the board, avoiding obstacles
        tx, ty = 0, h - 1 if sx <= (w - 1) // 2 else h - 1  # deterministic fallback (top-left bias)

    # Choose move maximizing progress to target, with obstacle repulsion and keeping away from opponent when equal
    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        curd = md(sx, sy, tx, ty)
        nd = md(nx, ny, tx, ty)
        progress = curd - nd
        # repulsion near obstacles
        rep = 0
        for ax, ay in obstacles:
            dd = md(nx, ny, ax, ay)
            if dd == 0:
                rep -= 50
            elif dd == 1:
                rep -= 8
            elif dd == 2:
                rep -= 3
        # if progress ties, prefer being closer than opponent to target
        od = md(ox, oy, tx, ty)
        myd = nd
        sway = (od - myd)
        s = progress * 100 + rep + sway * 2
        # keep deterministic tie-break: favor (dx,dy) with smallest lexicographic among best
        if s > best_s or (s == best_s and best is not None and (dx, dy) < best):
            best_s = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]