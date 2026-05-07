def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not resources or not legal:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds <= do:
            key = (0, ds, -do, rx, ry)
        else:
            key = (1, do - ds, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    curr_self = cheb(sx, sy, rx, ry)
    curr_opp = cheb(ox, oy, rx, ry)

    best_move = None
    best_mkey = None
    for dx, dy, nx, ny in legal:
        ns = cheb(nx, ny, rx, ry)
        no = cheb(ox, oy, rx, ry)  # opponent position unchanged this turn
        key = (ns, -no, 0 if ns < curr_self else 1, dx, dy)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]