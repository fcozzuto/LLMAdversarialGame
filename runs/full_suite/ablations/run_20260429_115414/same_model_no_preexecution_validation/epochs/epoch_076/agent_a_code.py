def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w // 2, h // 2)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Target: maximize (op_distance - self_distance), so we "deny" resources where we're closer.
    best_t = resources[0]
    best_s = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        sc = (do - ds) * 10 - ds  # primary deny margin, secondary quick pickup
        # slight bias to avoid hugging far-off edges
        sc += -abs(tx - (w - 1) / 2) * 0.05 - abs(ty - (h - 1) / 2) * 0.05
        if best_s is None or sc > best_s:
            best_s = sc
            best_t = (tx, ty)

    tx, ty = best_t
    # Choose move that decreases distance to target; tie-break by increasing deny margin vs opponent.
    cur_ds = cheb(sx, sy, tx, ty)
    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = cheb(nx, ny, tx, ty)
        ndm = cheb(ox, oy, tx, ty) - nds  # higher means better deny
        # Prefer strictly better distance; avoid stagnation unless it improves deny.
        stagn = 1 if nds == cur_ds else 0
        sc = (cur_ds - nds) * 100 + ndm * 5 - stagn * 0.5
        if best_score is None or sc > best_score:
            best_score = sc
            best_m = (dx, dy)

    # If somehow no valid moves (shouldn't happen), stay still.
    return [int(best_m[0]), int(best_m[1])]