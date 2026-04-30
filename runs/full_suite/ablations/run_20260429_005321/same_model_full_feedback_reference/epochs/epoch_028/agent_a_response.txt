def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def cheb_dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy - (dx < dy and dx * 2 or dy * 2) + (dx if dx > dy else dy)

    def step_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return (dx if dx > dy else dy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Obstacle proximity penalty (deterministic local avoid)
        adj_pen = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obstacles:
                adj_pen += 1
        # Choose move that maximizes advantage for some resource
        sc = -0.05 * step_dist(nx, ny, ox, oy) - 0.3 * adj_pen
        for rx, ry in resources:
            our_d = step_dist(nx, ny, rx, ry)
            opp_d = step_dist(ox, oy, rx, ry)
            # Prefer resources we can get earlier than opponent; otherwise deny by increasing opp advantage
            adv = opp_d - our_d
            sc = sc + (1e-6 if adv < 0 else 1) * (adv * 10) - 0.2 * our_d
        # Break ties by deterministic ordering
        if sc > best_sc or (sc == best_sc and (dx, dy) < best_mv):
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]