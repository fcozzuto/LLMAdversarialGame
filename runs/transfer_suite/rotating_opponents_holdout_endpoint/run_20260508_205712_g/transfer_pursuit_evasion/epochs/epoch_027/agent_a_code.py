def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = observation.get("resources", None)
    remaining = observation.get("remaining_resource_count", None)
    target = (ox, oy)
    if isinstance(remaining, (int, float)) and remaining > 0 and resources:
        best = None
        bestd = None
        for r in resources:
            if isinstance(r, dict):
                x = r.get("x", None)
                y = r.get("y", None)
            else:
                x = r[0] if isinstance(r, (list, tuple)) and len(r) > 0 else None
                y = r[1] if isinstance(r, (list, tuple)) and len(r) > 1 else None
            if x is None or y is None:
                continue
            rx, ry = int(x), int(y)
            if not inb(rx, ry):
                continue
            d = cheb(sx, sy, rx, ry)
            if bestd is None or d < bestd:
                bestd = d
                best = (rx, ry)
        if best is not None:
            target = best

    if target == (sx, sy):
        if inb(sx, sy):
            return [0, 0]

    tx, ty = target
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        role = (observation.get("self_role", "") or "").lower()
        chasing = ("pursu" in role) or (role == "pursuer") or ("agent" not in role)
        # If chasing: minimize distance to target, keep away from opponent slightly.
        # Otherwise: also minimize distance to target, but allow a bit more closeness.
        key = (d_to_t, -d_to_o) if chasing else (d_to_t, d_to_o)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]