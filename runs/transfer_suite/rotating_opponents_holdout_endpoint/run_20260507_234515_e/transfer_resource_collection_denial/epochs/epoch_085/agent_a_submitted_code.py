def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target():
        best = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                tx, ty = int(r[0]), int(r[1])
                if not inb(tx, ty):
                    continue
                d1 = cheb(sx, sy, tx, ty)
                if d1 > 7:
                    continue
                d2 = cheb(ox, oy, tx, ty)
                gain = d2 - d1
                key = (gain, -d1, -tx, -ty)
                if best is None or key > best[0]:
                    best = (key, tx, ty)
        if best is None:
            for r in resources:
                if isinstance(r, (list, tuple)) and len(r) >= 2:
                    tx, ty = int(r[0]), int(r[1])
                    if inb(tx, ty):
                        d1 = cheb(sx, sy, tx, ty)
                        d2 = cheb(ox, oy, tx, ty)
                        gain = d2 - d1
                        key = (gain, -d1, -tx, -ty)
                        if best is None or key > best[0]:
                            best = (key, tx, ty)
        if best is None:
            return None
        return best[1], best[2]

    if not resources or not inb(int(sx), int(sy)):
        return [0, 0]

    t = best_target()
    if t is None:
        return [0, 0]
    tx, ty = t

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (None, -10**9, 10**9, 10**9)
    for dx, dy in deltas:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        gain = d_opp - d_self
        key = (gain, -d_self, -abs(nx - tx), -abs(ny - ty), -dx, -dy)
        if key > (best_move[1], best_move[2], best_move[3], best_move[4], best_move[5] if best_move[0] is not None else 0, best_move[6] if best_move[0] is not None else 0):
            best_move = (dx, gain, -d_self, -abs(nx - tx), -abs(ny - ty), -dx, -dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(-(-0 + (0)))] if best_move[0] is not None else [0, 0]