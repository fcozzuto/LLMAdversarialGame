def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not inb(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if inb(sx + dx, sy + dy):
                    return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        return abs(ax - bx) if abs(ax - bx) >= abs(ay - by) else abs(ay - by)

    if not res:
        best = (10**9, 10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny):
                    continue
                dres = cheb(nx, ny, ox, oy)
                cand = (-dres, abs(dx) + abs(dy), dx, dy)
                if cand < (best[0], best[1], best[2], best[3]):
                    best = (cand[0], cand[1], dx, dy)
        return [best[2], best[3]]

    # Choose a target resource that we can likely reach first.
    # Prefer: (opp_reach_time - our_reach_time) large; then smaller our time; then stable tie by coords.
    best_t = None
    best_key = None
    for rx, ry in res:
        d_our = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # If equal reach, slightly prefer resources far from opponent (reduces contest).
        key = (-(d_opp - d_our), d_our, cheb(ox, oy, rx, ry), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        our_next = cheb(nx, ny, tx, ty)
        opp_next = cheb(ox, oy, tx, ty)

        # Primary: reduce our distance to target; secondary: keep away from opponent while not wasting steps.
        # Also, if opponent would be closer (already contested), bias to moves that increase their delay.
        primary = our_next - opp_next
        opp_dist = cheb(nx, ny, ox, oy)

        # Lexicographic: maximize primary, then maximize opp_dist, then minimize our_next, then tie-break by dx,dy.
        score = (-(primary), -opp_dist, our_next, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]