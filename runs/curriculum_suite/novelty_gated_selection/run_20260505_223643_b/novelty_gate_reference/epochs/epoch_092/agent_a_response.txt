def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # Fallback: move to maximize distance from opponent (deterministic)
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            val = man(nx, ny, ox, oy)
            if val > best[1]:
                best = ((dx, dy), val)
        return list(best[0] if best[0] is not None else (0, 0))

    # Choose move that improves our access to resources while discouraging opponent proximity
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # distance to closest resource from next position
        d_me = min(man(nx, ny, rx, ry) for rx, ry in resources)
        # opponent distance to closest same resources (min over resources to approximate contest pressure)
        d_op = min(man(ox, oy, rx, ry) for rx, ry in resources)

        # Bonus if moving reduces contest more than it helps opponent
        val = (-d_me) + 0.55 * (d_op)  # larger is better: closer to me, farther from opponent
        # Small tie-break: prefer moving direction that reduces distance to "best for me" resource
        if d_me == 0:
            val += 1000
        elif val > best_val:
            # add deterministic secondary: align to nearest resource from current pos
            target = min(resources, key=lambda rr: man(sx, sy, rr[0], rr[1]))
            d0 = man(target[0], target[1], nx, ny) - man(target[0], target[1], sx, sy)
            val += -0.01 * d0

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]