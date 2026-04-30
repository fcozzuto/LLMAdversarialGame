def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        resources = [(ox, oy)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose target: maximize advantage over opponent to reach it
    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        key = (od - sd, -sd, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Prefer moves that reduce own distance; break ties by also limiting opponent improvement
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        # Opponent potential improvement if they move optimally next (estimate by their current cheb - minimal next cheb)
        # Use their best immediate cheb after one move (small local set).
        best_od2 = None
        for pdx, pdy in moves:
            px, py = ox + pdx, oy + pdy
            if inb(px, py):
                d2 = cheb(px, py, tx, ty)
                if best_od2 is None or d2 < best_od2:
                    best_od2 = d2
        if best_od2 is None:
            best_od2 = cheb(ox, oy, tx, ty)

        od1 = cheb(ox, oy, tx, ty)
        opp_improve = od1 - best_od2  # higher means opponent gets closer
        # Also add slight preference for moving toward top-left deterministically to avoid ties.
        score = (sd2 * 10 + opp_improve, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]