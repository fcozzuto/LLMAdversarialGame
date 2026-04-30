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

    def obs_risk(x, y):
        r = 0
        for (bx, by) in obstacles:
            if cheb(x, y, bx, by) <= 1:
                r += 1
        return r

    # Choose target that I can reach relatively sooner; late game prefers closest.
    best_t = None
    best_v = None
    for (rx, ry) in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = (opd - myd)
        risk = obs_risk(rx, ry)
        val = (adv * 10) - (risk * (6 if not late else 3))
        if late:
            val += (20 - myd * 3)
        if best_v is None or val > best_v or (val == best_v and (myd < cheb(sx, sy, best_t[0], best_t[1]) if best_t else True)):
            best_v = val
            best_t = (rx, ry)

    tx, ty = best_t

    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Move selection: reduce distance; prefer lower local risk; slight bias to beat opponent.
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        local_r = obs_risk(nx, ny)
        score = -myd2 * 5 - local_r * (8 if not late else 5) + (opd2 - myd2) * 2
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]