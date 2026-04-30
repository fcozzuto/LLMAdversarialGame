def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx = (w - 1) if sx < (w - 1) - ox else 0
        ty = (h - 1) if sy < (h - 1) - oy else 0
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sc = -cheb(nx, ny, tx, ty) + 0.1 * cheb(nx, ny, ox, oy)
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best_target = None
    best_adv = -10**9
    best_selfd = 10**9
    for rx, ry in resources:
        selfd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        adv = oppd - selfd  # prefer places we are closer to
        if adv > best_adv or (adv == best_adv and selfd < best_selfd):
            best_adv = adv
            best_selfd = selfd
            best_target = (rx, ry)

    rx, ry = best_target
    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        new_selfd = cheb(nx, ny, rx, ry)
        new_oppd = cheb(nx, ny, ox, oy)
        sc = -new_selfd + 0.12 * new_oppd  # also keep away from opponent
        if sc > best[0]:
            best = (sc, dx, dy)

    return [best[1], best[2]]