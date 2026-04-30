def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_r = None
        best_sc = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; lightly favor closer routes.
            sc = (do - ds) * 100 - ds - (do <= ds) * 50
            if sc > best_sc or (sc == best_sc and (rx, ry) < (best_r[0], best_r[1]) if best_r else False):
                best_sc = sc
                best_r = (rx, ry)
        tx, ty = best_r

        cur_best = None
        cur_sc = -10**18
        # Evaluate next-step advantage toward the chosen target.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            ds2 = cheb(nx, ny, tx, ty)
            do2 = cheb(ox, oy, tx, ty)
            # Also consider not giving up advantage to opponent.
            sc = (do2 - ds2) * 100 - ds2 - (ds2 >= do2) * 50
            # Tie-break deterministically: closer to target, then smaller dx/dy lexicographically.
            if sc > cur_sc:
                cur_sc = sc
                cur_best = (dx, dy)
            elif sc == cur_sc and cur_best is not None:
                if ds2 < cheb(sx + cur_best[0], sy + cur_best[1], tx, ty) or (ds2 == cheb(sx + cur_best[0], sy + cur_best[1], tx, ty) and (dx, dy) < cur_best):
                    cur_best = (dx, dy)
        if cur_best is not None:
            return [int(cur_best[0]), int(cur_best[1])]

    # Fallback: no resources or no valid move found (shouldn't happen). Move toward center, away from opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dcen = cheb(nx, ny, cx, cy)
        do = cheb(nx, ny, ox, oy)
        sc = -dcen * 10 + do
        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]