def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    ax = (w - 1) // 2
    ay = (h - 1) // 2

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if resources:
            best_adv = -10**9
            best_selfd = 10**9
            best_oppsd = 10**9
            for rx, ry in resources:
                if (rx, ry) in occ:
                    continue
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                adv = od - sd
                if adv > best_adv or (adv == best_adv and (sd < best_selfd or (sd == best_selfd and od < best_oppsd))):
                    best_adv = adv
                    best_selfd = sd
                    best_oppsd = od

            # maximize advantage; if tied, minimize our distance; avoid letting opponent get too close
            key = (best_adv, -best_selfd, -cheb(ox, oy, nx, ny), -cheb(nx, ny, ax, ay))
        else:
            # no resources: drift toward center while keeping away from opponent
            key = (-cheb(nx, ny, ax, ay), cheb(ox, oy, nx, ny))
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]