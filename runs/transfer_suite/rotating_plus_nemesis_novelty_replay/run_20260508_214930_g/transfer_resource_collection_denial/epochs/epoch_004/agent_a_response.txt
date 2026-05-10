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

    def is_blocked(x, y):
        return (x, y) in obstacles

    # Target: maximize how much closer we are than opponent; tie by proximity and then a fixed preference.
    best_t = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        diff = od - sd  # positive: we are closer
        score = (diff, -sd, -(abs(rx - (w - 1)) + abs(ry - (h - 1))), rx + ry)
        if best_t is None or score > best_t[0]:
            best_t = (score, rx, ry)
    _, tx, ty = best_t

    # Candidate moves (including staying) in deterministic order.
    moves = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0), (0, 0), (1, 0),
        (-1, 1), (0, 1), (1, 1)
    ]

    # Evaluate next step by improvement toward target and ability to avoid being worse than opponent.
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or is_blocked(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        diff = nod - nsd
        # Prefer collecting sooner (small nsd), and prefer moves that keep us closer overall.
        # Slight tie-break: smaller remaining distance to far corner (deterministic).
        corner_dist = abs(nx - (w - 1)) + abs(ny - (h - 1))
        score = (diff, -nsd, -corner_dist, dx, dy)
        if best_m is None or score > best_m[0]:
            best_m = (score, dx, dy)

    if best_m is None:
        return [0, 0]
    return [best_m[1], best_m[2]]