def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx if dx >= 0 else -dx if dx < 0 else dx  # keep deterministic int ops
    # Fix cheb deterministically without floats
    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Depth-1 evaluation: choose move that maximizes "race gap" to the closest resource
    best_move = [0, 0]
    best_val = None
    opp_pos = (ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        npos = (nx, ny)
        self_best = 10**9
        opp_best = 10**9
        for r in res:
            d_s = dist(npos, r)
            if d_s < self_best:
                self_best = d_s
            d_o = dist(opp_pos, r)
            if d_o < opp_best:
                opp_best = d_o

        # Prefer taking a resource now; otherwise win the distance race after this move.
        if npos in res:
            val = (10**8, -self_best)  # strongly favor immediate capture
        else:
            # Larger is better: smaller self_best and larger opp_best.
            # Tie-break by absolute self_best (prefer closer) then lex via move ordering later.
            val = (opp_best - self_best, -self_best)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move