def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = [(int(x), int(y)) for x, y in resources]
    if not res:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for rx, ry in res:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources I'm not farther from; then closest to me; then farthest from opponent.
            score = (1 if md > od else 0, md, -od, rx, ry)
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        mdn = cheb(nx, ny, tx, ty)
        odn = cheb(ox, oy, tx, ty)
        # Prefer reducing distance; if tie, prefer move where I stay competitive vs opponent.
        competitive = 0 if mdn <= odn else 1
        val = (competitive, mdn, -(cheb(nx, ny, ox, oy)), abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    if not inb(sx, sy):
        # Shouldn't happen, but stay safe deterministically.
        return [0, 0]
    return best_move