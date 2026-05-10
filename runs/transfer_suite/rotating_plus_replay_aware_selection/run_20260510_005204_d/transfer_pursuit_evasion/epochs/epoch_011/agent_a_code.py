def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    res = observation.get("resources", None)
    resources = []
    if isinstance(res, list):
        for r in res:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                resources.append((int(r[0]), int(r[1])))
            elif isinstance(r, dict) and "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    role = str(observation.get("self_role", "")).lower()
    evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("hide" in role)

    if resources:
        best_target = None
        best_d = None
        for tx, ty in resources:
            d = cheb(sx, sy, tx, ty)
            if best_d is None or d < best_d:
                best_d = d
                best_target = (tx, ty)
        tx, ty = best_target
    else:
        tx, ty = None, None

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)
        val = 0
        if evader:
            val += 10 * d_op
            if tx is not None:
                val += -cheb(nx, ny, tx, ty)
        else:
            if tx is not None:
                val += 10 * (-cheb(nx, ny, tx, ty))
            val += -2 * max(0, 2 - d_op)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]