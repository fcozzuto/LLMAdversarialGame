def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def res_score(rx, ry):
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Strongly prefer resources where we're at least as close as opponent;
        # break ties by preferring nearer resources and slightly avoiding opponent row/col races.
        closer_bonus = 120 if myd <= opd else -20
        same_line_pen = 0
        if rx == ox or ry == oy:
            same_line_pen = 8
        return (opd - myd) * 160 + closer_bonus - myd - same_line_pen

    tx, ty = max(resources, key=lambda r: res_score(r[0], r[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best = None
    bestv = -10**18
    for dx, dy, nx, ny in legal:
        myd2 = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer increasing our lead and reducing our distance to the target.
        v = (opd - myd2) * 170 - myd2
        # Mild anti-stall: discourage staying unless it improves lead/distance.
        if dx == 0 and dy == 0:
            v -= 3
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]