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
    if not resources:
        return [0, 0]

    try:
        rem = int(observation.get("remaining_resource_count"))
    except:
        rem = len(resources)
    late = rem <= 4

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def near_obstacle_pen(x, y):
        p = 0
        for (bx, by) in obstacles:
            if cheb(x, y, bx, by) <= 1:
                p += 2
        return p

    best_r = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Aim for a resource where we are closer than opponent; in late game just minimize our distance.
        adv = (do - ds)  # higher is better
        if late:
            score = -ds - near_obstacle_pen(rx, ry) * 0.1
        else:
            score = adv * 10 - ds - near_obstacle_pen(rx, ry) * 0.25
        if best_score is None or score > best_score or (score == best_score and (rx, ry) < best_r):
            best_score = score
            best_r = (rx, ry)

    tx, ty = best_r

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Prefer moves reducing our distance; if late, also keep improving our advantage.
        val = -d_self
        if not late:
            val += (d_opp - d_self) * 0.5
        val -= cheb(nx, ny, ox, oy) * 0.05  # slight anti-clump
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]