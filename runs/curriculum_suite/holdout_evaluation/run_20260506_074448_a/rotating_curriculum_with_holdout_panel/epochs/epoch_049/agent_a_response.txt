def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def edge_pen(x, y):
        d = min(x, y, w - 1 - x, h - 1 - y)
        return -d * 0.05  # slight preference away from edges

    # Pick a target resource where we have tempo advantage; if tied, pick more central.
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        my_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        adv = opp_d - my_d
        cent = -((rx - cx) ** 2 + (ry - cy) ** 2)
        key = (-(adv), -(cent), my_d)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    rx, ry = best_r

    # Choose move that best advances to target while maintaining/creating advantage.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_after = man(nx, ny, rx, ry)
        opp_after = man(nx, ny, ox, oy)
        opp_to_target_after = man(ox, oy, rx, ry)

        # advantage if we reach target sooner than opponent (using opponent static distance)
        adv_after = opp_to_target_after - my_after

        # prefer moves that don't get too close to opponent unless it also increases adv
        closeness = -man(nx, ny, ox, oy)
        cent = -((nx - cx) ** 2 + (ny - cy) ** 2)

        score = (
            adv_after * 10.0
            + (-my_after) * 2.5
            + closeness * 0.15
            + cent * 0.01
            + edge_pen(nx, ny)
            + (-(dx * dx + dy * dy)) * 0.001  # slight prefer fewer/softer moves when equal
            + (0.0)
        )

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]