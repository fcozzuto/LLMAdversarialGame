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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    res = [(int(r[0]), int(r[1])) for r in resources]

    # Choose a target we can reach earlier (or that blocks opponent).
    best_t = res[0]
    best_k = None
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Higher is better: we want (od - sd), then smaller sd, then closer to us corner-ish deterministically
        k = (od - sd, -sd, -cheb(tx, ty, 0, 0))
        if best_k is None or k > best_k:
            best_k = k
            best_t = (tx, ty)
    tx, ty = best_t

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    res_set = set(res)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        val = 0
        if (nx, ny) in res_set:
            val += 10000
        # Move to target; strong preference to be earlier than opponent
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        val += (od - sd) * 200
        val += -sd * 5
        # If we can also immediately deny opponent from any nearby resource, prefer that
        # (check resources within 1 move of opponent after they would move: use current opponent pos only)
        for rx, ry in res:
            if cheb(ox, oy, rx, ry) <= 1 and (rx, ry) != (nx, ny):
                val += -50 if cheb(nx, ny, rx, ry) > 1 else 20
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]