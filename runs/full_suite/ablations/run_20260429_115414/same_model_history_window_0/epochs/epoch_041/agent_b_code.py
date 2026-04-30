def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Pick a resource where we are relatively closer than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_self = dist2(sx, sy, rx, ry)
        d_opp = dist2(ox, oy, rx, ry)
        # Higher priority for being much closer; tie-break by overall closeness.
        key = (-(d_opp - d_self), d_self)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key

    if best is None:
        # No resources: move to center slightly.
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    # Try move that reduces distance to target while avoiding obstacles.
    deltas = [[-1, -1], [0, -1], [1, -1],
              [-1, 0], [0, 0], [1, 0],
              [-1, 1], [0, 1], [1, 1]]
    cur_d = dist2(sx, sy, tx, ty)
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist2(nx, ny, tx, ty)
        # Prefer improvement, then avoid letting opponent get closer to the same target.
        opp_nd = dist2(ox, oy, tx, ty)
        opp_closer_penalty = nd - opp_nd  # deterministic small influence
        candidates.append((nd, - (cur_d - nd), opp_closer_penalty, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort()
    return [candidates[0][3], candidates[0][4]]