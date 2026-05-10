def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            if isinstance(p, dict) and "x" in p and "y" in p:
                x, y = int(p["x"]), int(p["y"])
            else:
                continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    role = str(observation.get("self_role") or observation.get("role") or "").lower()
    evader = ("evader" in role) or ("escape" in role)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    best_move = moves[4]
    if evader:
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
            d1 = cheb(nx, ny, ox, oy)
            # two-step escape heuristic: after our move, assume opponent can respond greedily
            best_op = 10**9
            for odx, ody in moves:
                tx, ty = ox + odx, oy + ody
                if not valid(tx, ty):
                    tx, ty = ox, oy
                d2 = cheb(nx, ny, tx, ty)
                if d2 < best_op:
                    best_op = d2
            # Prefer larger distance while also avoiding "stall" too long near obstacles
            val = d1 + 1.2 * best_op + 0.05 * (nx + ny)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        best_val = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
            d1 = cheb(nx, ny, ox, oy)
            # two-step chase heuristic: assume evader tries to maximize distance
            worst_ev = -10**9
            for edx, edy in moves:
                tx, ty = ox + edx, oy + edy
                if not valid(tx, ty):
                    tx, ty = ox, oy
                d2 = cheb(nx, ny, tx, ty)
                if d2 > worst_ev:
                    worst_ev = d2
            val = (d1) - 1.0 * worst_ev + 0.01 * (nx - ny)
            if val < best_val:
                best_val = val
                best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]