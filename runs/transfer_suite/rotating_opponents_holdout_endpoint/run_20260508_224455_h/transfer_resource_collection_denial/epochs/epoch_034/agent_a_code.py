def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Pick best target resource by current advantage; deterministic tie-breaks.
    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds
        # Prefer positive adv; then smaller self distance; then larger opponent distance; then deterministic.
        key = (0 if adv > 0 else 1, -adv, ds, -do, rx * 131 + ry * 17)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best[1], best[2]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_new = man(nx, ny, tx, ty)
        do_new = man(ox, oy, tx, ty)  # opponent position unchanged this turn
        adv_new = do_new - ds_new
        # Maximize advantage; then minimize self distance; then move deterministically.
        key = (-adv_new, ds_new, dx * 3 + dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is not None:
        return best_move

    # If all candidate moves are blocked, stay.
    return [0, 0]