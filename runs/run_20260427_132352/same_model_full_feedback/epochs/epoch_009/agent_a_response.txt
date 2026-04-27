def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not inb(sx, sy):
        return [0, 0]

    # Pick a target where we are relatively closer than opponent (advantage).
    # If all are poor, still pick the best available.
    best = None
    best_adv = None
    for x, y in resources:
        d1 = cheb(sx, sy, x, y)
        d2 = cheb(ox, oy, x, y)
        adv = d2 - d1
        # Slight preference for nearer targets to reduce wandering.
        val = (adv * 100) - (d1 * 2) - (d2 * 0.3)
        if best is None or val > best:
            best = val
            best_adv = (x, y)
    if best_adv is None:
        # No visible resources: head toward center while avoiding obstacles.
        best_adv = (w // 2, h // 2)

    tx, ty = best_adv

    # If opponent is much closer to target, try to "intercept" by moving toward a point
    # between us and target, nudging along the line from opponent to target.
    myd = cheb(sx, sy, tx, ty)
    opd = cheb(ox, oy, tx, ty)
    if myd > opd + 1:
        ix = (tx + ox) // 2
        iy = (ty + oy) // 2
        if inb(ix, iy) and (ix, iy) not in obst:
            tx, ty = ix, iy

    # Score candidate moves with obstacle safety and target improvement.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)  # opponent move unknown
        # Prefer reducing distance to chosen point; penalize moving away.
        score = (myd - myd2) * 10 - myd2
        # If we can step onto a resource immediately, strongly prefer it.
        if (nx, ny) in resources:
            score += 1000
        # Slightly discourage giving opponent an easy path by moving away from them too much.
        # (Helps when both chase same side resources.)
        score -= cheb(nx, ny, ox, oy) * 0.1
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]