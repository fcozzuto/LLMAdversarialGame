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

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obstacle_pressure(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    cnt += 1
        return cnt

    best = None
    best_score = -10**18
    target_center = ((w - 1) // 2, (h - 1) // 2)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        step_pen = obstacle_pressure(nx, ny)
        if resources:
            s = -step_pen * 0.5
            for rx, ry in resources:
                me = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                if me == 0:
                    s += 1000
                # Prefer resources where we are closer; otherwise deny by approaching still-reachable ones.
                adv = opd - me
                # If opponent is already adjacent, don't waste on that unless also immediate.
                if opd <= 1 and me > 1:
                    adv -= 3
                s += adv * 25 - me * 2 + (1 if cheb(nx, ny, rx, ry) <= 2 else 0)
                # Tiny deterministic bias to avoid ties oscillating
                s += (-rx - 3 * ry) * 1e-6
        else:
            tx, ty = target_center
            s = -cheb(nx, ny, tx, ty) - step_pen * 0.5
        if s > best_score:
            best_score = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]