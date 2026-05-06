def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best_t = None
    best_k = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        # Race/deny: prefer resources I'm at least as close to; otherwise sprint to their closest.
        advantage = opd - myd
        k = (0 if myd == 0 else 1, 0 if myd <= opd else 1, myd + (0 if myd <= opd else 3 * max(0, opd - myd)), -advantage)
        if best_k is None or k < best_k:
            best_k = k
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Denial bias: reduce my distance to the contested target, avoid giving opponent an easy path by moving away from their position when tied.
        tie_bias = md(nx, ny, ox, oy) if myd == 0 else 0
        val = (myd, -opd, tie_bias)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]