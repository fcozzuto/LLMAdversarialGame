def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_target = None
    best_tscore = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can beat; still consider closer ones even if behind.
        tscore = (do - ds) * 10 - ds
        if tscore > best_tscore:
            best_tscore = tscore
            best_target = (rx, ry)

    if best_target is None:
        # No visible resources: either hold position or move to reduce opponent distance.
        target = (ox, oy)
    else:
        target = best_target

    tx, ty = int(target[0]), int(target[1])

    best_move = (0, 0)
    best_mscore = -10**18
    base_opp = cheb(ox, oy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_next = cheb(nx, ny, tx, ty)
        do_now = base_opp
        # Primary: improve our advantage to the chosen target; Secondary: avoid moving into being too close to opponent.
        mscore = (do_now - ds_next) * 10 - ds_next
        # Slightly prefer moves that also increase distance from opponent (keeps us safer while contesting).
        mscore += cheb(nx, ny, ox, oy) * 0.1
        if mscore > best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]