def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    def dsq(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Pick a target where we are (ideally) closer than opponent; otherwise chase best remaining edge.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dsq(sx, sy, rx, ry)
        od = dsq(ox, oy, rx, ry)
        adv = od - sd  # higher is better
        key = (-adv, sd, rx, ry)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Choose move that maximizes advantage if we go toward the target (opponent assumed not moving this turn).
    # Also avoid moving into obstacles/out-of-bounds.
    best_m = None
    best_m_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd2 = dsq(nx, ny, tx, ty)
        od2 = dsq(ox, oy, tx, ty)
        adv2 = od2 - sd2
        # Prefer moves that increase advantage; then reduce distance; then deterministic order.
        key = (-adv2, sd2, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]