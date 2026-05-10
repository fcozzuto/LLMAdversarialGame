def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if W <= 0 or H <= 0:
        return [0, 0]
    obs_set = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs_set.add((int(o[0]), int(o[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Evaluate each immediate move by its best "capture advantage" over all remaining resources.
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        # Prefer moving onto resources immediately.
        immediate = 0
        for (rx, ry) in resources:
            if rx == nx and ry == ny:
                immediate = 1000000
                break
        if immediate:
            key = (-(immediate), 0)
        else:
            # Choose the resource where we are most likely ahead after this move.
            # Value increases when our distance is smaller than opponent's; break ties by closer to a resource.
            cur_best = None
            for rx, ry in resources:
                our_d = man(nx, ny, rx, ry)
                opp_d = man(ox, oy, rx, ry)
                # Opponent advantage if they are closer; our advantage when we are closer.
                adv = (opp_d - our_d)  # higher is better
                # Mild preference for shorter total travel to reduce stale targets.
                val = adv * 1000 - our_d
                if cur_best is None or val > cur_best[0] or (val == cur_best[0] and our_d < cur_best[1]):
                    cur_best = (val, our_d)
            # Higher cur_best[0] is better; invert for min-comparison key.
            key = (-cur_best[0], cur_best[1])
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    # If all candidate moves invalid (shouldn't happen), stay put.
    return best_move if best is not None else [0, 0]