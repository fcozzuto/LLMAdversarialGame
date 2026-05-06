def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_dist_to_self = man(ox, oy, sx, sy)
    target = None
    if resources:
        bestv = None
        for tx, ty in resources:
            md = man(sx, sy, tx, ty)
            od = man(ox, oy, tx, ty)
            # Prefer resources where we are closer than opponent, but still consider distance.
            v = (md - 0.85 * od) + 0.02 * (tx + ty)
            if bestv is None or v < bestv:
                bestv = v
                target = (tx, ty)
    if target is None:
        target = (w // 2, h // 2)

    # Prefer moves that reduce distance to target; add pressure to avoid getting too close to opponent,
    # but allow blocking if opponent is very close.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_to_t = man(nx, ny, target[0], target[1])
        d_to_opp = man(nx, ny, ox, oy)

        # If opponent is near, avoid stepping into adjacent squares (reduce collision/gets collected).
        avoid = 0
        if opp_dist_to_self <= 3 and d_to_opp <= 1:
            avoid = 50

        # If opponent is near a resource and we can intercept, lightly penalize squares that give them advantage.
        intercept = 0
        if resources and opp_dist_to_self <= 4:
            # Choose local intercept by estimating whether we worsen our relative position.
            od_here = man(nx, ny, target[0], target[1])
            intercept = 1.5 * (od_here - man(sx, sy, target[0], target[1]))

        score = d_to_t + 0.35 * d_to_opp + avoid + intercept
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]