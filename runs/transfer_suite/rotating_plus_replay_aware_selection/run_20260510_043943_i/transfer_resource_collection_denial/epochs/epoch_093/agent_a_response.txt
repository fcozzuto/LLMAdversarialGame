def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    targets = []
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not ok(rx, ry):
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # New tweak vs prior: heavily favor "safe" grabs where we are not behind by much,
        # and incorporate how quickly we can reduce the race (ds/do).
        safe_margin = do - ds
        speed = -(ds * 2 + (1 if do == ds else 0))
        # If opponent is much closer, down-rank this target.
        penalty = 0 if safe_margin >= -1 else (-(safe_margin) * 3)
        val = safe_margin * 10 + speed + penalty
        targets.append((val, -ds, rx, ry))

    if not targets:
        return [0, 0]

    targets.sort(reverse=True)
    _, _, tx, ty = targets[0]

    # If already on a resource, stay.
    if sx == tx and sy == ty:
        return [0, 0]

    # Choose a move that decreases our distance to the chosen target; break ties by
    # increasing opponent distance to that target, then by deterministic order.
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        # primary: minimize our distance; secondary: maximize opponent distance (slow their contest)
        key = (ds2, -do2, dy, dx)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]