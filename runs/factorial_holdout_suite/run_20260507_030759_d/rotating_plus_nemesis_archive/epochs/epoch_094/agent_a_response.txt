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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_inbounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick best resource by "opponent advantage": how much closer we are than them (negative is bad).
    best_targets = []
    best_adv = None
    for tx, ty in resources:
        selfd = cheb(sx, sy, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        adv = oppd - selfd
        if best_adv is None or adv > best_adv or (adv == best_adv and (selfd < best_selfd)):
            best_adv = adv
            best_selfd = selfd
            best_targets = [(tx, ty)]
        elif adv == best_adv and selfd == best_selfd:
            best_targets.append((tx, ty))
    tx, ty = best_targets[0]

    # Greedy step toward target with deterministic tie-breaks.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_inbounds(nx, ny):
            continue
        selfd2 = cheb(nx, ny, tx, ty)

        # Secondary goal: don't step onto resources that opponent is closer to (resource denial).
        deny = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                if cheb(ox, oy, rx, ry) <= cheb(nx, ny, rx, ry):
                    deny = 1
                break

        # Tie-break: prefer smaller distance, then prefer moves that increase our advantage.
        oppd2 = cheb(ox, oy, tx, ty)
        adv2 = oppd2 - selfd2
        key = (deny, selfd2, -adv2, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best