def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                res.append((x, y))

    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_rx, best_ry = None, None
    best_key = (-10**9, -10**9, 10**9)
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can arrive earlier (or at least not later), then closer.
        key = (do - ds, -(ds), -(rx + ry * 0))  # deterministic tie-break
        if key > best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move_key = (-10**9, -10**9, -10**9, 10**9)

    # Evaluate next step by improving our distance while maintaining advantage over opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; reflect it deterministically
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Encourage moves that increase the advantage (do2 - ds2), then reduce our distance, then stay stable.
        adv = do2 - ds2
        move_key = (adv, -(ds2), -(dx == 0 and dy == 0), (abs(dx) + abs(dy)))
        if move_key > best_move_key:
            best_move_key = move_key
            best = [dx, dy]

    return best if best is not None else [0, 0]