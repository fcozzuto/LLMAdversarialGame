def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_for_target(tx, ty):
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        centerx, centery = (W - 1) / 2.0, (H - 1) / 2.0
        center_bias = -0.03 * ((tx - centerx) ** 2 + (ty - centery) ** 2)
        return (opd - myd) + center_bias

    targets = resources if resources else [(int((W - 1) / 2), int((H - 1) / 2))]
    if resources:
        targets = sorted(resources, key=lambda t: (-score_for_target(t[0], t[1]), t[0], t[1]))[:4]
    else:
        targets = [(int((W - 1) / 2), int((H - 1) / 2))]

    def cell_block_penalty(x, y):
        # discourage stepping adjacent to obstacles
        pen = 0
        for ax, ay in obstacles:
            dx = abs(x - ax)
            dy = abs(y - ay)
            if dx <= 1 and dy <= 1 and (dx != 0 or dy != 0):
                pen += 0.25
        return pen

    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        my_best = -10**18
        for tx, ty in targets:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            center_bias = -0.02 * ((nx - (W - 1) / 2.0) ** 2 + (ny - (H - 1) / 2.0) ** 2)
            # prefer moves that reduce my distance and (indirectly) contest the resource
            val = (opd - myd) + center_bias - 0.6 * myd - 0.35 * cell_block_penalty(nx, ny)
            if val > my_best:
                my_best = val
        # slight tie-break toward staying near center
        tie = -0.001 * ((nx - (W - 1) / 2.0) ** 2 + (ny - (H - 1) / 2.0) ** 2)
        val = my_best + tie
        if val > best[2]:
            best = (dx, dy, val)

    return [int(best[0]), int(best[1])]