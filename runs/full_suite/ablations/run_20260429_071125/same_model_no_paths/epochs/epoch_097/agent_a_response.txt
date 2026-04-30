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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If resource at our tile, stay to secure it.
    if (sx, sy) in set(resources):
        return [0, 0]

    best_dx, best_dy = 0, 0
    best_val = -10**18

    # Precompute opponent distance to resources for speed.
    opp_ds = {}
    if resources:
        for rx, ry in resources:
            opp_ds[(rx, ry)] = cheb(ox, oy, rx, ry)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            # Evaluate move by best "capture pressure" against opponent at next tile.
            cur_best = -10**18
            nd = cheb(nx, ny, nx, ny)  # 0, just to keep deterministic ops simple
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = opp_ds[(rx, ry)]
                # Want ds small, do large; also prefer resources nearer.
                val = (do - ds) * 100 - ds - (cheb(ox, oy, rx, ry) - do) * 0 + nd
                # Strongly prefer immediate pickup.
                if ds == 0:
                    val += 10**9
                # If multiple are close, slight tie-break by closer to us.
                if ds <= 1:
                    val += 5
                if val > cur_best:
                    cur_best = val
            # Small deterrent if we step directly onto a resource where opponent is equally close.
            # (Encourages taking advantage gaps.)
            # Approx: compare best gap to second best via current best_val proxy.
            score = cur_best
        else:
            # No resources: maximize separation; prefer moving toward center.
            sep = cheb(nx, ny, ox, oy)
            cx, cy = (w - 1) // 2, (h - 1) // 2
            center = -cheb(nx, ny, cx, cy)
            score = sep * 10 + center

        # Prefer safer moves if scores tie: avoid getting adjacent to opponent too early.
        if score > best_val:
            best_val = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]