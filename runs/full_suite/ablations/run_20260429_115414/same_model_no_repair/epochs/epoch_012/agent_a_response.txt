def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def best_step_toward(px, py, tx, ty):
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, dx, dy)
        return (best[1], best[2]) if best[0] < 10**9 else (0, 0)

    if not resources:
        return [0, 0]

    # Target selection: deny where we can arrive no later; else chase the smallest lead deficit.
    best_t = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if myd <= opd:
            key = (0, -(opd - myd), -((rx + ry) / (w + h)), myd)
        else:
            key = (1, (myd - opd), -((rx + ry) / (w + h)), myd)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    best_move = (0, 0)
    best_score = -10**18

    # 1-ply simulate: my move, then opponent greedily toward target; maximize my advantage.
    for dx, dy in dirs:
        nsx, nsy = sx + dx, sy + dy
        if not inb(nsx, nsy):
            nsx, nsy = sx, sy
        myd2 = cheb(nsx, nsy, tx, ty)

        odx, ody = best_step_toward(ox, oy, tx, ty)
        nosx, nosy = ox + odx, oy + ody
        if not inb(nosx, nosy):
            nosx, nosy = ox, oy
        opd2 = cheb(nosx, nosy, tx, ty)

        score = (opd2 - myd2) * 1000 - myd2 - 0.1 * opd2
        # Minor deterministic tie-break toward reducing distance to center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0