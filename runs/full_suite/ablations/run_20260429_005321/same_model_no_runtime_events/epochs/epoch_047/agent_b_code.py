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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not ok(sx, sy):
        return [0, 0]

    # If standing on a resource, stay to secure deterministic behavior
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    # Choose best target by advantage over opponent
    best_t = None
    best_key = None  # (primary, our_d, adv, x, y)
    for (tx, ty) in resources:
        our_d = cheb(sx, sy, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        primary = 0 if our_d <= opp_d else 1
        adv = our_d - opp_d  # <=0 is good
        key = (primary, our_d, adv, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    if best_t is None:
        # No visible resources: head toward opponent to contest
        tx, ty = ox, oy
    else:
        tx, ty = best_t

    # Pick move that maximizes improvement in our distance and advantage
    cur_our = cheb(sx, sy, tx, ty)
    cur_opp = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        our_d = cheb(nx, ny, tx, ty)
        # approximate opponent move: assume opponent also greedily minimizes its distance to same target
        opp_best = cur_opp
        for odx, ody in dirs:
            px, py = ox + odx, oy + ody
            if ok(px, py):
                d = cheb(px, py, tx, ty)
                if d < opp_best:
                    opp_best = d
        opp_d_next = opp_best

        # Score: prefer reducing our distance; prefer keeping/increasing advantage
        score = (our_d, opp_d_next - our_d, -(our_d - cur_our), nx, ny, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]