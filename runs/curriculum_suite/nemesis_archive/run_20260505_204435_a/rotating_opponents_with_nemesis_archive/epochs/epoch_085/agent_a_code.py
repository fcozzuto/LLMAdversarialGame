def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def rep_cell(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (int(q[0]), int(q[1]))
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (int(r[0]), int(r[1]))
        return None
    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        return [0, 0]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)
    def neighbors(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                out.append((nx, ny))
        return out if out else [(x, y)]
    def opp_best_dist_to(target):
        tx, ty = target
        best = 10**9
        for nx, ny in neighbors(ox, oy):
            d = cheb(nx, ny, tx, ty)
            if d < best:
                best = d
        return best
    oppd = {t: opp_best_dist_to(t) for t in rpos}
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy
        val = -10**9
        for rx, ry in rpos:
            self_d = cheb(nx, ny, rx, ry)
            gain = oppd[(rx, ry)] - self_d
            if gain > val:
                val = gain
        val -= 0.05 * cheb(nx, ny, ox, oy)
        key = (val, -abs(dx), -abs(dy), dx, dy)
        bkey = (best_val, -abs(best_move[0]), -abs(best_move[1]), best_move[0], best_move[1])
        if key > bkey:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]