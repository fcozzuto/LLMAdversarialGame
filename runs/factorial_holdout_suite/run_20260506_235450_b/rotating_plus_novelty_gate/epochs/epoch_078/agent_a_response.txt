def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    valid_rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                valid_rs.append((x, y))
    if not valid_rs:
        return [0, 0]

    # Choose resource we are best positioned to secure first (advantage then proximity)
    best = None
    for cell in valid_rs:
        sd = md((sx, sy), cell)
        od = md((ox, oy), cell)
        adv = od - sd
        key = (adv, -sd, -(abs(cell[0] - ox) + abs(cell[1] - oy)))
        if best is None or key > best[0]:
            best = (key, cell)
    target = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_cost = None

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cost = (cheb(nx, ny, target[0], target[1]), md((nx, ny), target), (nx, ny) != (sx, sy))
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_move = [dx, dy]

    return best_move