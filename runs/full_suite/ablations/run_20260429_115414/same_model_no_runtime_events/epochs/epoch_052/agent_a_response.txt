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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem or 0)
    except:
        rem = 0
    late = rem <= 4

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_cell = None
    if resources:
        # Deterministic tie-breaking: prefer higher advantage; then closer to us; then lexicographically.
        cand = []
        for r in resources:
            sd = cheb((sx, sy), r)
            od = cheb((ox, oy), r)
            adv = od - sd  # positive means we are closer
            # In late game, just go nearest to avoid overfitting to "steals"
            score = (sd if late else -adv)
            # Create a single tuple score with lexicographic tie-break
            if late:
                t = (score, r[0], r[1])
            else:
                t = (score, -adv, sd, r[0], r[1])
            cand.append((t, r))
        cand.sort(key=lambda z: z[0])
        best_cell = cand[0][1]
    else:
        # No visible resources: stabilize near center while maintaining validity and slight bias away from opponent.
        center = (w // 2, h // 2)
        best_cell = center

    tx, ty = best_cell[0], best_cell[1]

    # Move greedily toward target; if blocked, try best alternative deterministically.
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb((nx, ny), (tx, ty))
        # In late game, minimize distance to target. Otherwise, also slightly prefer increasing distance from opponent.
        dist_op = cheb((nx, ny), (ox, oy))
        t = (dist, dist_op, dx, dy) if late else (dist, -dist_op, dx, dy)
        candidates.append((t, dx, dy))
    candidates.sort(key=lambda z: z[0])
    if candidates:
        return [int(candidates[0][1]), int(candidates[0][2])]

    return [0, 0]