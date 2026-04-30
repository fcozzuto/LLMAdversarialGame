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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def mobility(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                cnt += 1
        return cnt

    best_sc = -10**18
    best = (0, 0)
    # Deterministic tie-break: iterate moves in fixed order above.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        sc = 0.0

        # Immediate contest-aware targeting of resources.
        # If we can reach earlier than opponent, reward strongly; otherwise penalize.
        for rx, ry in resources:
            d_us = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)

            # Small penalty for being generally far; big swing for contest status.
            if d_us < d_op:
                sc += (18 - d_us) + (d_op - d_us) * 3.0
            elif d_us == d_op:
                sc -= 2.0 + d_us * 0.5
            else:
                sc -= (d_us - d_op) * 4.0 + d_us * 0.4

        # Avoid giving opponent a direct advantage by drifting toward our farthest corner.
        # (This is the strategic change vs pure greedy targeting.)
        sc += (mobility(nx, ny) * 1.5)

        # Mild separation from opponent to prevent them from stealing contests easily.
        sc += (cheb(nx, ny, ox, oy) * 0.2)

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]