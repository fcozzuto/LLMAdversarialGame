def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_move(dx, dy, target):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return -10**9
        tx, ty = target
        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        on_res = 1 if (nx, ny) == (tx, ty) else 0
        return (opp_d - our_d) + 0.2 * on_res - 0.01 * our_d

    if resources:
        best_t = None
        best_adv = -10**18
        best_our_d = 10**18
        for tx, ty in resources:
            our_d = cheb(sx, sy, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            adv = opp_d - our_d
            if adv > best_adv or (adv == best_adv and our_d < best_our_d):
                best_adv = adv
                best_our_d = our_d
                best_t = (tx, ty)
        if best_t is None:
            target = resources[0]
        else:
            target = best_t
    else:
        target = (w - 1, h - 1)

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        val = score_move(dx, dy, target)
        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]