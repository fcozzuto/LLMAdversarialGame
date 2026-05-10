def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        cx, cy = (w // 2, h // 2)
        tx, ty = (cx, cy)
    else:
        best_r = resources[0]
        best_v = -10**18
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            v = (do - ds) * 1000 - ds
            if ds == 0:
                v += 10**9
            # mild preference toward cells that are closer to opponent (force earlier contest)
            v += (rx * 3 + ry * 5) * 1e-6
            if v > best_v:
                best_v = v
                best_r = (rx, ry)
        tx, ty = best_r

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_cost = 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cost = man(nx, ny, tx, ty)
        # discourage moving into/near obstacles deterministically
        if (nx, ny) in obstacles:
            cost += 1000
        cost += (abs(nx - ox) + abs(ny - oy)) * 0.01
        # tie-break deterministically by direction order
        if cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]