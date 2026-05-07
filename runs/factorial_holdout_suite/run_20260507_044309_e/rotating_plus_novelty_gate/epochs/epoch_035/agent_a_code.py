def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        best_key = None
        for i, (dx, dy, nx, ny) in enumerate(valid):
            d = man(nx, ny, tx, ty)
            key = (d, i)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose move that maximizes collection advantage over opponent.
    # Tie-break: prefer faster nearest resource; deterministic ordering by index.
    best = None
    best_key = None
    res = [tuple(r) for r in resources]
    for i, (dx, dy, nx, ny) in enumerate(valid):
        best_adv = -10**9
        best_my_d = 10**9
        for rx, ry in res:
            my_d = man(nx, ny, rx, ry)
            op_d = man(ox, oy, rx, ry)
            adv = op_d - my_d  # positive means we are closer
            if my_d < best_my_d or (my_d == best_my_d and adv > best_adv):
                best_my_d = my_d
                best_adv = adv
        # Prefer larger advantage; also prefer smaller my distance (in case of similar adv)
        key = (-best_adv, best_my_d, i)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]]