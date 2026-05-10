def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target: first any resource we can secure no worse than opponent; else deny closest to opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if ds <= do:
            key = (0, (do - ds), ds, -rx, -ry)  # prefer larger advantage (smaller do-ds), then nearer
        else:
            key = (1, do, ds, rx, ry)  # prefer closest to opponent, then nearer for us
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_m = None
    best_v = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        ds_new = man(nx, ny, tx, ty)
        do_new = man(ox, oy, tx, ty)
        # Prefer reducing distance to target while improving our lead against opponent for that target.
        v = (ds_new, -(do_new - ds_new), man(nx, ny, ox, oy), dx, dy)
        if best_v is None or v < best_v:
            best_v = v
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]