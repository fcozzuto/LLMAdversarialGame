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
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    tx, ty = sx, sy
    best = -10**9
    if resources:
        for (rx, ry) in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; if not, pick one that maximizes our relative threat.
            score = (do - ds) * 10 - ds
            if score > best:
                best = score
                tx, ty = rx, ry
    else:
        tx, ty = w // 2, h // 2

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    def cand_steps():
        steps = []
        # Primary: move toward target
        steps.append((dx, dy))
        # Alternatives: try to preserve progress while avoiding obstacles
        if dx != 0 or dy != 0:
            steps.append((dx, 0))
            steps.append((0, dy))
            steps.append((dx, -dy))
            steps.append((-dx, dy))
        steps.append((0, 0))
        # keep unique and within bounds/obstacles
        seen = set()
        out = []
        for mx, my in steps:
            nx, ny = sx + mx, sy + my
            if (mx, my) not in seen and inside(nx, ny):
                seen.add((mx, my))
                out.append((mx, my))
        return out

    best_move = (0, 0)
    best_h = -10**9
    for mx, my in cand_steps():
        nx, ny = sx + mx, sy + my
        # New goal: get closer to our target AND optionally approach the opponent if they are closer to it.
        h = -cheb(nx, ny, tx, ty)
        # If opponent is currently closer to the chosen target, we try to "intercept" near it by also moving
        # to reduce their distance.
        h += -max(0, cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty)) * 2
        # Encourage not wandering: small preference for moving away from being corner-trapped
        h += -0.1 * (abs(nx - sx) + abs(ny - sy))
        if h > best_h:
            best_h = h
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]