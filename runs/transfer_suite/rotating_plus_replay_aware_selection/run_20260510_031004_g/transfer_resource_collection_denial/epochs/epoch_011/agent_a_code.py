def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res = [(int(p[0]), int(p[1])) for p in resources]

    def pick_opponent_target(px, py):
        best = None
        for tx, ty in res:
            d = cheb(px, py, tx, ty)
            # Opponent tends to sweep: it will prefer closer resources deterministically.
            key = (d, (tx + ty), tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        return best[1]

    txo, tyo = pick_opponent_target(ox, oy)
    best_od = None
    opp_next = (ox, oy)
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, txo, tyo)
        if best_od is None or d < best_od or (d == best_od and (nx, ny) < opp_next):
            best_od = d
            opp_next = (nx, ny)
    opx, opy = opp_next

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate this move by best "first-collector" opportunity.
        val = None
        for tx, ty in res:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(opx, opy, tx, ty)
            first = 1 if myd <= opd - 1 else 0
            # Slight preference for nearer resources if tie.
            score = first * 1000000 + (opd - myd) * 1000 - myd + (-(tx + ty) * 0.001)
            if val is None or score > val:
                val = score
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]