def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_pos = (ox, oy)
    self_pos = (sx, sy)

    # Choose a contested target: closer to us and farther from opponent.
    best_target = None
    best_target_score = None
    for r in resources:
        d_us = cheb(self_pos, r)
        d_op = cheb(opp_pos, r)
        # Higher is better: (opponent advantage) minus (our distance)
        score = (d_op - d_us)
        if best_target is None or score > best_target_score:
            best_target_score = score
            best_target = r

    if best_target is None:
        # No visible resources: bias toward our far corner from opponent
        tx = 0 if sx > w // 2 else w - 1
        ty = 0 if sy > h // 2 else h - 1
        best_target = (tx, ty)

    # Pick move that improves contested targeting; small tie-break toward resources.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ns = (nx, ny)
        d_us = cheb(ns, best_target)
        d_op = cheb(opp_pos, best_target)
        # Primary: maximize (d_op - d_us). Secondary: minimize distance to opponent (slightly block).
        val = (d_op - d_us) * 1000 - cheb(ns, opp_pos)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]