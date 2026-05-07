def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_towards(tx, ty):
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # Tie-break: prefer reducing distance to opponent to "denier-proof" against rushing
            do = cheb(nx, ny, ox, oy)
            # Deterministic ordering: encode move preference
            key = (d, do, dx, dy, nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # If no resources, do the least-bad move: maximize distance from opponent while staying safe
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            # Also prefer moving toward center a bit to avoid getting trapped by obstacles
            d_ctr = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
            key = (-d_opp, d_ctr, dx, dy, nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose a resource we can reach first; otherwise pick best swing that limits opponent advantage
    best_r = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer positive advantage; if tie, pick closest resource to us; then deterministic ordering
        adv = do - ds  # positive means we're closer (since cheb time)
        key = (-adv, ds, rx, ry)
        if best_r is None or key < best_r[0]:
            best_r = (key, rx, ry)

    rx, ry = best_r[1], best_r[2]
    return step_towards(rx, ry)