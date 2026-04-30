def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = []
    for p in (observation.get("resources") or []):
        x, y = p
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        best_val = -10**9
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, ox, oy)
            if v > best_val:
                best_val = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_target = None
    best_adv = -10**9
    any_we_closer = False
    for rx, ry in resources:
        ourd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - ourd
        if adv > 0:
            any_we_closer = True
            if adv > best_adv or (adv == best_adv and ourd < cheb(sx, sy, best_target[0], best_target[1]) if best_target else True):
                best_adv = adv
                best_target = (rx, ry)

    if not any_we_closer:
        best_target = resources[0]
        best_opd = cheb(ox, oy, best_target[0], best_target[1])
        for rx, ry in resources[1:]:
            opd = cheb(ox, oy, rx, ry)
            if opd < best_opd:
                best_opd = opd
                best_target = (rx, ry)

    tx, ty = best_target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in legal