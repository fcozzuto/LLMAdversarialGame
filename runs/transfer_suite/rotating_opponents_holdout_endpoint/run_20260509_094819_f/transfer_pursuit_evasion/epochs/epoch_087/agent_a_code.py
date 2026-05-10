def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in self_role) or (self_role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    prefer_capture = pursuer
    prefer_flee = not pursuer

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        if pursuer and nx == ox and ny == oy:
            return [dx, dy]
        if (not pursuer) and nx == ox and ny == oy:
            continue

        d = cheb(nx, ny, ox, oy)
        # small deterministic penalties to discourage getting boxed in
        neigh = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) not in blocked:
                neigh += 1

        # Key: lower is better for pursuer, higher is better for evader
        if pursuer:
            key = (d, -neigh)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        else:
            key = (d, neigh)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]