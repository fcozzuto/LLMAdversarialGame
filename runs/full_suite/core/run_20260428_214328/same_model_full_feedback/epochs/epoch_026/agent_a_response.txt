def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tiebreak: prefer moves closer to center, then lexicographic on dx,dy.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def score_pos(nx, ny):
        if not resources:
            # With no resources, drift toward center and slightly away from opponent.
            dc = cheb(nx, ny, int(cx), int(cy))
            do = cheb(nx, ny, ox, oy)
            return (1000 - do) - 0.1 * dc

        best = -10**9
        for rx, ry in resources:
            dself = cheb(nx, ny, rx, ry)
            dopp = cheb(ox, oy, rx, ry)
            # Primary: be closer than opponent (contested pickup chance).
            # Secondary: reduce own distance to that resource.
            # Tertiary: slight center preference to break ties.
            s = (dopp - dself) * 50 - dself - 0.01 * cheb(nx, ny, int(cx), int(cy))
            if s > best:
                best = s
        return best

    best_move = (0, 0)
    best_val = -10**18
    best_center = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        val = score_pos(nx, ny)
        cc = cheb(nx, ny, int(cx), int(cy))
        if val > best_val or (val == best_val and (cc < best_center or (cc == best_center and (dx, dy) < best_move))):
            best_val = val
            best_center = cc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]