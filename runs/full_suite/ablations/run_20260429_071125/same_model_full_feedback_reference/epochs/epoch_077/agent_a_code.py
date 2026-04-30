def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if (d, abs((nx - tx)) + abs((ny - ty)), -dx, -dy) < (best[0], best[1], best[2], best[3]):
                best = (d, abs(nx - tx) + abs(ny - ty), -dx, -dy)
        return [best[2] * -1, best[3] * -1]

    best_target = None
    best_key = None
    # Advantage: higher means opponent farther (good for us).
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        adv = d_opp - d_me
        key = (-adv, d_me, d_opp, rx, ry)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # One-step choose move that improves chance: minimize (d_me_next - d_opp_next) then d_me_next.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me_next = cheb(nx, ny, tx, ty)
        d_opp_next = cheb(ox, oy, tx, ty)
        score1 = d_me_next - d_opp_next
        cand = (score1, d_me_next, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best is None or cand < best:
            best = cand

    return [best[3], best[4]]