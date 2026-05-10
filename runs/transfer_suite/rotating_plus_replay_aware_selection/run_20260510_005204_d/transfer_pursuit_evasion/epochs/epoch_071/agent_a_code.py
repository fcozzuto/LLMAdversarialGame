def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "")).lower()
    we_evader = ("evader" in role) or ("runner" in role)
    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def around_obst_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            xi = x + dx
            if xi < 0 or xi >= w: 
                continue
            for dy in (-1, 0, 1):
                yj = y + dy
                if yj < 0 or yj >= h:
                    continue
                if (xi, yj) in blocked:
                    pen += 3 if dx == 0 and dy == 0 else 1
        return pen

    target_corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if we_evader:
        tx, ty = max(target_corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        # pursuer: target the opposite of evader-style corner, biases across map
        tx, ty = min(target_corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = None
    best_score = None
    # deterministic tie-break order
    deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        dist_op = cheb(nx, ny, ox, oy)
        dist_to_target = cheb(nx, ny, tx, ty)
        obst = around_obst_pen(nx, ny)
        if we_evader:
            # maximize separation and keep away from obstacles
            score = dist_op * 10 - obst * 2 - dist_to_target * 0.5
        else:
            # minimize separation and also discourage obstacles
            score = -dist_op * 10 - obst * 2 - dist_to_target * 0.1
        if best is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]