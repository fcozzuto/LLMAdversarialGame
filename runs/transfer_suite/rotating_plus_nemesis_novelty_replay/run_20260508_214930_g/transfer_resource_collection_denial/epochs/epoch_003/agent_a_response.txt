def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles_list = observation.get('obstacles', []) or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose target resource: maximize "advantage" (we closer or tied), then prefer nearer.
    best = None
    tx, ty = resources[0]
    for rx, ry in resources:
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        diff = opp_d - self_d  # higher means we are closer than opponent
        score = (diff, -self_d, -(abs(rx - (w - 1)) + abs(ry - (h - 1))), rx + ry)
        if best is None or score > best:
            best = score
            tx, ty = rx, ry

    # Greedy one-step toward target with obstacle-aware tie-break.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        self_next = cheb(nx, ny, tx, ty)
        opp_now = cheb(ox, oy, tx, ty)
        adv = opp_now - self_next
        # Prefer moves that keep us closer to target; slight preference for reducing opponent distance overall.
        val = (adv, -self_next, abs((nx + ny) - (tx + ty)), 0 if (dx == 0 and dy == 0) else 1)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]