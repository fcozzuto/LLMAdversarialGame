def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    tx, ty = None, None
    if resources:
        best_sd = None
        best_do = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                cx, cy = r[0], r[1]
                if not (isinstance(cx, int) and isinstance(cy, int)):
                    continue
                sd = cheb(sx, sy, cx, cy)
                od = cheb(ox, oy, cx, cy)
                if best_sd is None or sd < best_sd or (sd == best_sd and od > best_do):
                    best_sd = sd
                    best_do = od
                    tx, ty = cx, cy

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if tx is None:
            score = cheb(nx, ny, ox, oy)
        else:
            dt = cheb(nx, ny, tx, ty)
            do = cheb(nx, ny, ox, oy)
            score = -dt * 10 + do
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]