def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        best = (0, 0)
        best_sc = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sc = -cheb(nx, ny, tx, ty) + 0.01 * cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]]

    res_set = set(resources)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose the resource that maximizes our competitive advantage from next position.
        local_best = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Big bonus if we can step onto it now.
            step_bonus = 1000 if (nx, ny) == (rx, ry) else 0
            sc = step_bonus + (d_op - d_me) * 50 - d_me
            # Slightly prefer resources in "my direction" vs opponent direction
            sc += 0.1 * (cheb(nx, ny, sx, sy) == 0 and 0 or 0)  # deterministic no-op
            if sc > local_best:
                local_best = sc

        # Secondary: avoid moving into squares that make us clearly farther from all resources.
        # (approximated by distance to closest resource from next)
        closest = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < closest:
                closest = d
        safety = 0.5 * (closest == 0 and 0 or -closest)

        # Tertiary: keep a small preference for moves that reduce distance to opponent
        # only when competitive resource advantage is similar.
        opp_close = cheb(nx, ny, ox, oy)

        total = local_best + safety - 0.01 * opp_close
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]