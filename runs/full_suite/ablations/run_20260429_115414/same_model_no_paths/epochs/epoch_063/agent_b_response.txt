def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_adj(x, y):
        c = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    best_t = None
    if resources:
        best_adv = None
        best_mdist = None
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - md  # positive => I am closer
            if (best_adv is None or adv > best_adv or (adv == best_adv and (best_mdist is None or md < best_mdist))):
                best_adv = adv
                best_mdist = md
                best_t = (rx, ry)
    else:
        best_t = (w // 2, h // 2)

    tx, ty = best_t

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    my_d0 = cheb(sx, sy, tx, ty)
    my_prev = my_d0

    best = None
    best_val = None
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # Encourage getting closer; discourage leaving target; slight contest pressure.
        val = (my_prev - myd) * 3.0 + (oppd - cheb(ox, oy, tx, ty)) * 0.0
        # Contention: if I move closer relative to opponent's current distance.
        val += (cheb(ox, oy, tx, ty) - myd) * 0.8
        # Obstacle pressure: avoid crowded adjacency.
        val += -1.2 * obs_adj(nx, ny)
        # Prefer staying roughly oriented toward target (avoid random).
        val += -0.15 * cheb(nx, ny, sx, sy)
        # If on resource, prioritize strongly.
        if resources and (nx, ny) in resources:
            val += 1000.0
        # Tie-break deterministically by move order and lexicographic delta.
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]