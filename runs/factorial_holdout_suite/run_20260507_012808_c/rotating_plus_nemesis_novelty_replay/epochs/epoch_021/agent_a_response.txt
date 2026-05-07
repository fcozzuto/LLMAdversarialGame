def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev

    my = (sx, sy)
    opp = (ox, oy)

    best = None
    for rx, ry in resources:
        d_me = dist(my, (rx, ry))
        d_op = dist(opp, (rx, ry))
        adv = d_op - d_me
        key = (adv, -d_me, - (rx == sx and ry == sy), -(rx + ry))
        if best is None or key > best[0]:
            best = (key, (rx, ry), d_me, d_op)

    (_, (tx, ty), _, _) = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand_order = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0),
                   (-dx, 0), (0, -dy), (-dx, -dy)]
    best_step = (0, 0)
    best_score = None

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    for cdx, cdy in cand_order:
        nx, ny = sx + cdx, sy + cdy
        if not valid(nx, ny):
            continue
        nd = dist((nx, ny), (tx, ty))
        # Prefer reducing distance, then avoiding positions where opponent is closer to same target
        score = (-(nd), dist(opp, (tx, ty)) - nd, -abs((nx - tx)) - abs((ny - ty)))
        if best_score is None or score > best_score:
            best_score = score
            best_step = (cdx, cdy)

    return [int(best_step[0]), int(best_step[1])]