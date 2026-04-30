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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        best_for_move = -10**9
        # Choose a target resource to maximize "being earlier than opponent"
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer closer resources; heavily penalize giving opponent the lead
            lead = do - ds  # positive means we are closer (or equal if 0)
            val = -ds * 3 + lead * 8
            # Encourage cutting off: if we are not ahead, still prefer contested picks that are close
            if lead < 0:
                val -= (-lead) * 10
            # Slight tie-break: prefer moving toward center-ish to reduce wall trapping
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dist_center = cheb(nx, ny, int(cx), int(cy))
            val -= dist_center * 0.2
            if val > best_for_move:
                best_for_move = val

        if best_val is None or best_for_move > best_val:
            best_val = best_for_move
            best_move = (dx, dy)
        elif best_for_move == best_val:
            # Deterministic tie-break: prefer not increasing manhattan to opponent (avoid pointless chasing)
            curd = abs(nx - ox) + abs(ny - oy)
            bestnx, bestny = sx + best_move[0], sy + best_move[1]
            bestd = abs(bestnx - ox) + abs(bestny - oy)
            if curd < bestd:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]