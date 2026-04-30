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

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def obstacle_pen(x, y):
        # discourage stepping near obstacles; strong penalty if on obstacle (shouldn't happen)
        pen = 0
        if blocked(x, y):
            return 10**6
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if blocked(x + dx, y + dy):
                    pen += 6
        return pen

    # choose move that maximizes advantage over opponent in reaching a resource
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        # advantage: smaller (my_dist - opp_dist) is good; maximize negative
        my_to_op = cheb(nx, ny, ox, oy)
        total = 0
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # prefer taking resources where we are closer than opponent
            # also bias toward nearer resources overall
            score = (d_op - d_my) * 10 - d_my * 0.5
            # avoid getting too close to opponent if no immediate advantage
            if d_my > 0 and d_op <= d_my:
                score -= 0.25 * my_to_op
            total += score / (1 + d_my)
        val = total - obstacle_pen(nx, ny)

        # tie-break deterministically: prefer moves toward opponent corner
        if best is None or val > best_val or (val == best_val and cheb(nx, ny, ox, oy) < cheb(best[0], best[1], ox, oy)):
            best_val = val
            best = (nx, ny)

    if best is None:
        return [0, 0]
    return [best[0] - sx, best[1] - sy]