def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, head toward center to improve future options
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        best_sc = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            sc = -cheb(nx, ny, tx, ty) + 0.05 * cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    # Choose the resource with maximum self-advantage; break ties by urgency
    best_target = resources[0]
    best_adv = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = ds - do  # smaller means we are closer; we want minimize this
        if best_adv is None or adv < best_adv or (adv == best_adv and ds < cheb(sx, sy, best_target[0], best_target[1])):
            best_adv = adv
            best_target = (rx, ry)

    rx, ry = best_target

    # Move one step to maximize immediate progress to chosen target while considering opponent distance
    best = None
    best_sc = -10**18
    cur_ds = cheb(sx, sy, rx, ry)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nds = cheb(nx, ny, rx, ry)
        ndo = cheb(ox, oy, rx, ry)  # opponent position fixed for this step
        # Primary: reduce distance to target; Secondary: keep/extend advantage; Tertiary: avoid stepping toward opponent
        sc = 100 * (cur_ds - nds) - 10 * (nds - ndo)
        sc += 0.1 * cheb(nx, ny, ox, oy)
        # If we can potentially match/beat opponent by next step, boost
        if nds <= ndo:
            sc += 25
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]] if best else [0, 0]