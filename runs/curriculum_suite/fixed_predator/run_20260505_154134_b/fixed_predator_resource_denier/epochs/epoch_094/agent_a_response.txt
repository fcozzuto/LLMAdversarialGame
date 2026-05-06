def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx)
            e = abs(ny - ty)
            dd = d if d > e else e
            key = (dd, nx + ny)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_adv = None
        best_selfd = None
        best_oppd = None
        best_tie = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            # choose resource giving maximal advantage; tie-break by faster self, then resource order
            if best_adv is None or adv > best_adv or (adv == best_adv and (sd < best_selfd or (sd == best_selfd and (rx, ry) < best_tie))):
                best_adv = adv
                best_selfd = sd
                best_oppd = od
                best_tie = (rx, ry)
        # overall: prioritize advantage; if tied, prioritize self proximity; then prefer moving towards center for stability
        center_d = cheb(nx, ny, w // 2, h // 2)
        key = (-best_adv, best_selfd, center_d, nx + 100 * ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]