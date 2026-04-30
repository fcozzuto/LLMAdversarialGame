def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # If somehow inside obstacle, deterministically escape
    if not free(sx, sy):
        for dx, dy in [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick resource with best opponent-vs-self distance advantage, then closest to self
    best = None  # (adv, selfd, x, y)
    for x, y in resources:
        selfd = cheb(sx, sy, x, y)
        oppd = cheb(ox, oy, x, y)
        adv = oppd - selfd
        cand = (adv, selfd, x, y)
        if best is None or cand > best:
            best = cand
    _, _, tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**9, 10**9, 10**9, 0, 0)
    curd = cheb(sx, sy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer decreasing distance; break ties with deterministic lex order.
        score = (nd - curd, nd, - (abs(nx - ox) + abs(ny - oy)), dx, dy)
        if score < best_move:
            best_move = score

    return [int(best_move[3]), int(best_move[4])]