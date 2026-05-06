def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def cell_ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if best is None or v > best[0]:
                best = (v, dx, dy)
        return [0 if best is None else best[1], 0 if best is None else best[2]]

    # Score each move by best resource it lets us reach first; tie-break by denying opponent.
    best = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        best_for_move = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            # Encourage taking resources we can reach soon, and denying those opponent is near.
            reach = -sd
            deny = od
            val = (adv, reach, -deny)
            if best_for_move is None or val > best_for_move:
                best_for_move = val
        if best is None or best_for_move > best[0]:
            best = (best_for_move, dx, dy)
    return [0 if best is None else best[1], 0 if best is None else best[2]]