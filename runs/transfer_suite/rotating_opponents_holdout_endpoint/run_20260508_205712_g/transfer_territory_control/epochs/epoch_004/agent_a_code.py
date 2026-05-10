def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    unclaimed = observation.get("unclaimed_cells", None)
    if unclaimed is None:
        unclaimed = []
    unclaimed = [tuple(p) for p in (unclaimed or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Prefer capturing cells near opponent.
    best = None
    best_key = None
    for x, y in unclaimed:
        if (x, y) in obstacles or not inb(x, y):
            continue
        near_opp = abs(x - ox) + abs(y - oy) <= 2
        d = abs(x - sx) + abs(y - sy)
        key = (0 if near_opp else 1, d, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    if best is None:
        # Fallback: move away from obstacles toward board center deterministically.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx, ty = cx, cy
    else:
        tx, ty = best

    # Choose the allowed step that minimizes distance to target, avoiding obstacles.
    chosen = (0, 0)
    chosen_key = None
    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # small penalty for not moving
        d = abs(nx - tx) + abs(ny - ty)
        key = (d, 0 if (dx == 0 and dy == 0) else 1, nx, ny)
        if chosen_key is None or key < chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]