def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_score = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue

            # Evaluate move by the best resource we are likely to beat.
            # Prefer resources where we have advantage vs opponent (by distance).
            move_best = -10**18
            for rx, ry in resources:
                myd = d2(nx, ny, rx, ry)
                opd = d2(ox, oy, rx, ry)
                # advantage: smaller myd and larger opd
                # plus slight tie-break to steer toward nearer-than-current and avoid dead zones
                adv = (opd - myd) - 0.1 * myd + 0.02 * (rx - (w - 1) / 2) * (rx - (w - 1) / 2) * 0
                # if resource is immediately reachable, strong boost
                if myd == 0:
                    adv += 10**9
                if adv > move_best:
                    move_best = adv

            # Secondary preference: keep some separation from opponent to avoid them taking the same next resource.
            sep = d2(nx, ny, ox, oy)
            score = move_best + 0.001 * sep
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # No resources visible: move toward center while keeping away from obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = -d2(nx, ny, cx, cy) + 0.001 * d2(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]