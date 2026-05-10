def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = obstacles_list if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Deterministic evaluation: after moving, choose the resource that maximizes advantage
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Pick target for THIS next position: prefer resources with largest (opp_dist - self_dist)
        # Tie-break: smaller self_dist, then farther coords to reduce mirrored dithering.
        best_adv = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds
            key = (adv, -ds, rx, ry)  # maximize adv, then minimize ds (via -ds), then deterministic
            if best_adv is None or key > best_adv[0]:
                best_adv = (key, (rx, ry), ds, do)

        (adv_key, (tx, ty), ds, do) = best_adv
        # Move quality: closer to target, but keep advantage primary; discourage no-op when equally good
        dist_to_target = man(nx, ny, tx, ty)
        key = (adv_key[0], -dist_to_target, -do, -abs(tx - ox) - abs(ty - oy), 0 if (dx == 0 and dy == 0) else 1, dx, dy)
        if best is None or key > best[0]:
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]