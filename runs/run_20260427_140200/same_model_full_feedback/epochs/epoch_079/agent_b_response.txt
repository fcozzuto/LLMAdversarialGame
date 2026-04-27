def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def resource_value(rx, ry, mx, my):
        myd = cheb(mx, my, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources I'm at least as close to; otherwise try to pick resources that slow them down.
        advantage = (opd - myd)
        # Higher is better; closer is better; being closer than opponent is strongly rewarded.
        return (advantage * 3) - myd + (opd - myd)

    best_move = (0, 0)
    best_score = -10**18

    # If no resources known, move toward center while avoiding obstacles.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = -cheb(nx, ny, tx, ty)
                if score > best_score:
                    best_score = score
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate best reachable resource from next position.
        # Also add a small "denial" term: if a resource is closer to opponent than to me, avoid helping them.
        maxv = -10**18
        denial = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            v = (opd - myd) * 3 - myd
            if v > maxv:
                maxv = v
            if opd < myd:
                denial += (myd - opd)
        score = maxv - 0.4 * denial - 0.05 * cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]