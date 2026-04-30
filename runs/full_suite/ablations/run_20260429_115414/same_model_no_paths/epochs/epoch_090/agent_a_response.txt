def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    target = None
    best_rel = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer where I'm closer than opponent; also nudge toward central area.
        rel = (opd - myd) * 100 - (myd * 3) - (abs(rx - cx) + abs(ry - cy)) * 0.01
        # Deterministic tie-break: lexicographic
        if rel > best_rel + 1e-12 or (abs(rel - best_rel) <= 1e-12 and (target is None or (rx, ry) < target)):
            best_rel = rel
            target = (rx, ry)

    if target is None:
        # No resources visible: keep moving to reduce distance to center while avoiding obstacles.
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, int(cx), int(cy)) + (cheb(nx, ny, ox, oy) * 0.01)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Main: improve relative claim; Secondary: move toward target; Tertiary: keep away from opponent.
        val = (opd - myd) * 100 - myd * 6 + cheb(nx, ny, ox, oy) * 0.2
        if resources:
            # Small penalty if this step makes opponent closer to the same target (proxy).
            opp_step_d = cheb(ox, oy, tx, ty)
            val -= 0.05 * opp_step_d
        if val > best_val + 1e-12 or (abs(val - best_val) <= 1e-12 and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]