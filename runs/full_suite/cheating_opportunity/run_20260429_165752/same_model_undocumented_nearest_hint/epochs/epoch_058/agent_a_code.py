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

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order already fixed by list.
    best_move = (0, 0)
    best_val = -10**18

    # Strategy: for each move, evaluate best "swing" on any reachable resource:
    # value = (opp_dist - my_dist) - 0.1*resource_distance_to_center
    # plus obstacle risk: avoid stepping adjacent to obstacles.
    center_x, center_y = (W - 1) / 2.0, (H - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        myd_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            swing = (opd - myd)
            # Prefer closer-to-center resources slightly to reduce pathing dead-ends.
            center_bias = 0.1 * (abs(rx - center_x) + abs(ry - center_y))
            val = swing - center_bias

            # Add a small bonus if move brings us closer than opponent to that resource.
            if myd < opd:
                val += 0.25

            if val > myd_best:
                myd_best = val

        # Obstacle adjacency penalty (local, deterministic)
        risk = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    risk += 1
        myd_best -= 0.15 * risk

        # Small preference to move toward opponent when neutral (helps contest).
        if myd_best == 0:
            myd_best -= 0.001 * cheb(nx, ny, ox, oy)

        if myd_best > best_val:
            best_val = myd_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]