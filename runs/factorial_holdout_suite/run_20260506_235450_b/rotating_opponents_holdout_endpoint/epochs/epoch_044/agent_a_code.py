def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        x = y = None
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x = y = None
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, drift toward farthest corner from opponent to reduce contest.
    if not resources:
        tx, ty = (0, 0) if (sx > w - 1 - sx) else (w - 1, h - 1)
        if ox <= w - 1 - ox:
            tx, ty = w - 1, h - 1
        best = (0, 0)
        bestv = 10**9
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = dist_cheb(nx, ny, tx, ty)
                if v < bestv:
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = 10**18

    # Choose move by maximizing our lead on contested resources.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # compute best target resource preference under opponent pressure
        local_best = 10**18
        for rx, ry in resources:
            ds = dist_cheb(nx, ny, rx, ry)
            do = dist_cheb(ox, oy, rx, ry)
            # If opponent is closer, penalize strongly; otherwise reward.
            # Deterministic: no randomness; tie by resulting value.
            v = ds - 2.5 * (do - ds)  # ds - 2.5*(do-ds)= ds +2.5*(ds-do)
            if v < local_best:
                local_best = v

        # Small secondary objective: keep distance from opponent to reduce denier interference.
        sep = dist_cheb(nx, ny, ox, oy)
        val = local_best - 0.08 * sep
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]