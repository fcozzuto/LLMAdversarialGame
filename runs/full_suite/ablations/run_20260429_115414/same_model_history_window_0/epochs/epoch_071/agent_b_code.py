def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    w, h = observation["grid_width"], observation["grid_height"]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource that we can reach sooner than the opponent (deterministic tie-breaks)
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer positive reach advantage; then closest to us; then farthest from opponent
        key = (-(do - ds), ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else (sx, sy)
    # If no resources, just drift toward center
    if best is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Greedy one-step: avoid obstacles/bounds, reduce distance to target; small penalty for moving away from it.
    cur_d = dist((sx, sy), (tx, ty))
    best_step = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        # Secondary: reduce opponent access (prefer not to give them better approach to our target)
        nd_op = dist((ox, oy), (tx, ty))
        val = (nd, -nd_op, abs(dx) + abs(dy), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_step = (dx, dy)

    # If greedy doesn't improve at all (stuck), try a deterministic escape: move that minimizes obstacle pressure by best distance anyway
    if best_step == (0, 0) and best_val is not None and best_val[0] > cur_d:
        # fallback: pick move with minimal nd regardless (already done), so just return best_step
        return [best_step[0], best_step[1]]

    return [best_step[0], best_step[1]]