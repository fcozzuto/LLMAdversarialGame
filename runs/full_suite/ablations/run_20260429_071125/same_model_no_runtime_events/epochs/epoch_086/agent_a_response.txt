def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Select a target resource: prefer ones we can reach strictly earlier.
    if resources:
        best = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Higher score is better; prioritize earlier arrival, then smaller ds, then deterministic coords.
            key = (0 if ds < do else 1, ds - do, ds, tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        tx, ty = best[1]
    else:
        # Fallback: move toward opponent's corner to contest space
        tx, ty = 0 if ox > w // 2 else w - 1, 0 if oy > h // 2 else h - 1
        if not valid(tx, ty):
            tx, ty = ox, oy

    cur_ds = cheb(sx, sy, tx, ty)
    cur_do = cheb(ox, oy, tx, ty)

    # Choose move that maximizes improvement vs opponent distance to the same target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cur_do  # opponent doesn't move this turn
        # Value: want to reduce our distance and (if close) also reduce potential loss by increasing separation.
        # Also keep moving rather than wasting turns unless already optimal.
        val = (ns < cur_ds, cur_ds - ns, no - ns, -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]