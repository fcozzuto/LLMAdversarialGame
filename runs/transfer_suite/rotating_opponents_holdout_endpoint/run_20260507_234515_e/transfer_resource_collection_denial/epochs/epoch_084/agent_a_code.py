def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    candidates = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if not inb(tx, ty):
                continue
            d_me = cheb(sx, sy, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # prefer resources we can arrive at first; otherwise prefer those denying opponent access
            score = (d_op - d_me) * 10 - d_me
            candidates.append((score, tx, ty, d_me, d_op))
    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True, key=lambda z: z[0])
    _, tx, ty, _, _ = candidates[0]

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in neigh:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny):
            continue
        d_new = cheb(nx, ny, tx, ty)
        # slight preference for moves that also increase our lead against opponent
        d_op = cheb(ox, oy, tx, ty)
        val = (d_op - d_new) * 10 - d_new
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]