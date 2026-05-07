def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach no later than opponent, then with largest lead.
        key = (0, ds) if ds <= do else (1, do - ds, ds)
        # Convert to maximization by using negative of "badness":
        # For ds<=do: smaller ds is better.
        # For ds>do: larger lead against opponent is better (do-ds big), then smaller ds.
        if ds <= do:
            score = (0, -0, -ds)  # always choose ds<=do over ds>do; then smaller ds
        else:
            score = (1, -(do - ds), -ds)
        if best_key is None or score > best_key:
            best_key = score
            best = (tx, ty)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny):
                moves.append((dx, dy, nx, ny))

    # Choose move that most reduces distance to target; tie-break deterministically.
    cur_d = cheb(sx, sy, tx, ty)
    chosen = None
    chosen_key = None
    for dx, dy, nx, ny in moves:
        nd = cheb(nx, ny, tx, ty)
        # Prefer greater reduction; if equal, prefer smaller nd; then deterministic ordering.
        key = (-(nd - cur_d), -nd, dx, dy)
        if chosen_key is None or key > chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]