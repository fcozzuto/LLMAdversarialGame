def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    legal.sort()
    opp_bias = 3  # discourage moving toward resources opponent is closer to
    best_move = legal[0]
    best_val = None

    if not resources:
        # fallback: head toward center to reduce worst-case
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            val = cheb(nx, ny, tx, ty)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        cur = cheb(nx, ny, ox, oy) * 0  # deterministic placeholder: no effect
        best_res = None
        best_dist = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # prefer resources we can reach sooner; penalize if opponent is closer
            score = myd + (opp_bias if opd < myd else 0) + (0 if (rx, ry) == (nx, ny) else 0)
            if best_dist is None or score < best_dist:
                best_dist = score
                best_res = (rx, ry)
        # tie-break by slightly preferring moves that decrease distance to chosen resource
        rx, ry = best_res
        val = best_dist * 10 + (cheb(sx, sy, rx, ry) - cheb(nx, ny, rx, ry))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]