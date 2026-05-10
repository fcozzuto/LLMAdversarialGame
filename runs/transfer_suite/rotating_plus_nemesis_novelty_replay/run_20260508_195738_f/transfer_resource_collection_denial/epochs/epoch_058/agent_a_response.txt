def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        ax, ay = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        best = (-10**9, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = cheb(nx, ny, ax, ay) * -1 + cheb(nx, ny, ox, oy) * 0.02
            if v > best[0]:
                best = (v, (dx, dy))
        return [best[1][0], best[1][1]]

    opp_best = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
    best = (-10**18, (0, 0))
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_best = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        margin = opp_best - my_best
        # Tie-break: move toward a resource while slightly dispersing from opponent
        to_opp = cheb(nx, ny, ox, oy)
        v = margin * 100 - my_best * 3 + to_opp * 0.05
        if v > best[0]:
            best = (v, (dx, dy))
    return [best[1][0], best[1][1]]