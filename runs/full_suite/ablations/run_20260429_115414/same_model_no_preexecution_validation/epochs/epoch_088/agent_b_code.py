def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_pen(x, y):
        # Lower is better; penalize being adjacent to obstacles
        pen = 0
        for (oxb, oyb) in obstacles:
            if abs(oxb - x) <= 1 and abs(oyb - y) <= 1:
                pen += 3
        return pen

    # Target: resource where we are most relatively closer than opponent; tie-break on self distance then coords.
    best = None
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (-(od - md), md, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # If obstacle blocks direct approach, this local move choice tends to slide around.
    best_move = None
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_after = cheb(nx, ny, tx, ty)
            # Advantage pressure plus obstacle avoidance and small preference to reduce both axes (diagonal ok).
            md_now = cheb(sx, sy, tx, ty)
            adv = cheb(ox, oy, tx, ty) - d_after
            step_improve = md_now - d_after
            val = ( -adv, d_after, obs_pen(nx, ny), -(dx == 0 and dy == 0), -(abs(dx) + abs(dy)) )
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]