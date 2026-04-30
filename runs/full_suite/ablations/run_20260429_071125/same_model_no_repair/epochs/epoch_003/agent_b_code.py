def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = W - 1 - sx, H - 1 - sy  # head toward center-ish from our corner via symmetry
        if (W - 1) - sx < W // 2:
            tx = W - 1
        if (H - 1) - sy < H // 2:
            ty = H - 1

    def best_dists(px, py):
        my_near = 10**9
        op_near = 10**9
        for rx, ry in resources:
            d1 = cheb(px, py, rx, ry)
            if d1 < my_near: my_near = d1
            d2 = cheb(ox, oy, rx, ry)
            if d2 < op_near: op_near = d2
        if my_near == 10**9:
            my_near = 0
        if op_near == 10**9:
            op_near = 0
        return my_near, op_near

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_near, op_near = best_dists(nx, ny)
        opp_dist = cheb(nx, ny, ox, oy)
        # Primary: increase relative claimability (opponent nearest - my nearest)
        # Secondary: avoid giving opponent immediate proximity
        val = (op_near - my_near) * 10 - opp_dist
        # Tertiary: slight bias toward improving closeness to the most valuable resource for us
        if resources:
            local_best = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                adv = cheb(ox, oy, rx, ry) - d
                key = (-adv, d, rx, ry)
                if local_best is None or key < local_best[0]:
                    local_best = (key, (rx, ry))
            val += -local_best[0][1]
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]