def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not (isinstance(sx, int) and isinstance(sy, int) and 0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, x, y):
        dx = abs(x - a)
        dy = abs(y - b)
        return dx if dx > dy else dy

    def best_target():
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = r[0], r[1]
            if not (isinstance(tx, int) and isinstance(ty, int) and inb(tx, ty)):
                continue
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = od - sd
            # prefer bigger advantage, then closer to us, then deterministic coordinate
            key = (-adv, sd, tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        return None if best is None else best[1]

    target = best_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    # Choose among legal moves the one that decreases distance to target;
    # if tied, pick move that increases opponent distance; if still tied, deterministic order.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in oset:
                continue
            sd = cheb(nx, ny, tx, ty)
            od = cheb(nx, ny, ox, oy)
            # Note: opponent distance to target approx uses its position; use (opp->target) too
            oppd = cheb(ox, oy, tx, ty)
            score = (sd, -oppd, nx, ny)
            moves.append((score, [dx, dy]))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0])
    return moves[0][1]