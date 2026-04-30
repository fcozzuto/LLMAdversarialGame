def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: nearest resource to self (if any), else go toward opponent.
    if resources:
        tx, ty = resources[0]
        bestd = cheb(sx, sy, tx, ty)
        for rx, ry in resources[1:]:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                tx, ty = rx, ry
    else:
        tx, ty = ox, oy

    # Evaluate moves: go to target, and also try to prevent opponent from approaching it faster.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_to_t = cheb(nx, ny, tx, ty)
        opp_to_t = cheb(ox, oy, tx, ty)

        # Resource pressure: compare how much we reduce our distance to nearest resource vs. how much opponent has.
        if resources:
            my_near = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < my_near: my_near = d
            opp_near = 10**9
            for rx, ry in resources:
                d = cheb(ox, oy, rx, ry)
                if d < opp_near: opp_near = d
        else:
            my_near = my_to_t
            opp_near = opp_to_t

        # Anti-rush: try to increase opponent distance while moving toward target.
        my_to_opp = cheb(nx, ny, ox, oy)

        # Score: prioritize reaching resources, then deny opponent access, then avoid getting adjacent.
        val = 0
        val += -3.0 * my_near
        val += 2.0 * (opp_near - my_near)  # deny
        val += 0.25 * my_to_opp
        val += -0.1 * my_to_t

        # Small deterministic tie-break toward reducing distance to opponent if equal.
        if val > best_val + 1e-12:
            best_val = val
            best_move = (dx, dy)
        elif abs(val - best_val) <= 1e-12:
            if cheb(sx + best_move[0], sy + best_move[1], ox, oy) > my_to_opp:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]