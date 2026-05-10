def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    def obst_near(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    if not resources:
        return [0, 0]

    # Sweep-row opponent assumption: likely prioritizes resources on its current row.
    # Counter by biasing away from opponent row unless we can clearly win the same target.
    best_rx, best_ry = None, None
    best_key = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not valid(rx, ry):
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        row_pen = 0 if ry != oy else 3  # avoid opponent's likely sweep row
        # If we can already be closer than opponent, row penalty matters less.
        lead = (od - sd)
        win_bias = 0 if lead >= 0 else 2
        # Prefer fewer obstacle-adjacent tiles near the resource.
        near_pen = obst_near(rx, ry)
        # Build a deterministic minimization key (lexicographic).
        key = (
            row_pen + win_bias + near_pen,     # smaller is better
            sd - lead * 0.25,                 # prefer larger lead, then closer
            cheb(sx, sy, rx, ry),             # tiebreaker
            rx, ry
        )
        if best_key is None or key < best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry

    # Greedy next step with obstacle avoidance: pick valid move that most reduces our distance,
    # with deterministic direction tie-break.
    dirs = [
        (0, 0),
        (1, 0), (0, 1), (-1, 0), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    best = (10**9, 10**9, 10**9, 0, 0)
    curd = man(sx, sy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        # Primary: distance reduction; Secondary: avoid stepping near obstacles; Tertiary: reduce opponent advantage locally.
        red = curd - nd
        near = obst_near(nx, ny)
        oppd = man(ox, oy, tx, ty)
        # Prefer stronger pursuit while also avoiding risky squares.
        key = (-red, near, abs(nx - tx) + abs(ny - ty), dx, dy, nd, oppd)
        if key < best:
            best = key
    return [int(best[3]), int(best[4])]