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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_score = -10**18

    has_res = bool(resources)
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    current_best = 0
    if has_res:
        for rx, ry in resources:
            d = man(sx, sy, rx, ry)
            if current_best == 0 or d < current_best:
                current_best = d

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if has_res:
            mind = None
            on_res = False
            for rx, ry in resources:
                if rx == nx and ry == ny:
                    on_res = True
                    mind = 0
                    break
                d = man(nx, ny, rx, ry)
                if mind is None or d < mind:
                    mind = d
            if on_res:
                score += 100000
            else:
                score += -mind * 50
                if mind < current_best:
                    score += 500
                elif mind == current_best:
                    score += 100
        else:
            tx, ty = w // 2, h // 2
            score += -man(nx, ny, tx, ty)

        # avoid getting too close to opponent unless we can take a resource now
        od = man(nx, ny, ox, oy)
        score += od * 2
        if resources and (nx, ny) not in resources:
            score -= od == 0  # deterministic tiny discouragement (effectively none)

        if score > best_score:
            best_score = score
            best_move = [int(dx), int(dy)]

    return best_move