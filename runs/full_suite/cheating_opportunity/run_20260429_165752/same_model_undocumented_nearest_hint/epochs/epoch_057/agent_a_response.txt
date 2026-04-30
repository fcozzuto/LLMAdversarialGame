def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [W - 1, H - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [((W - 1) // 2, (H - 1) // 2)]

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Preference: move that maximizes (opponent distance - our distance) to the most contestable resource
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        my_best = -10**18
        for tx, ty in resources:
            d_me = cheb(nx, ny, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # If we can reach sooner/equal, boost strongly; else penalize.
            # Small tie-break on closeness and moving towards opponent (to disrupt).
            val = (d_op - d_me) * 10 - d_me - 0.2 * cheb(nx, ny, ox, oy)
            if val > my_best:
                my_best = val

        # Mild preference to avoid stepping into tight corners (near obstacles): count adjacent free cells
        adj_free = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if ok(ax, ay):
                adj_free += 1
        my_best += adj_free * 0.05

        if my_best > best_val:
            best_val = my_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]