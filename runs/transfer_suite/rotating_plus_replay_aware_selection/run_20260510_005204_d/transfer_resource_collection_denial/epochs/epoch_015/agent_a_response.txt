def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose the resource that maximizes our "temporal advantage" (opponent farther than us).
    best_target = None
    best_key = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        adv = opd - myd
        center_bias = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        # Tie-break: prefer closer resources with more guaranteed advantage.
        key = (adv, -myd, center_bias, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)
    tx, ty = best_target

    # Evaluate one-step moves with obstacle avoidance and local opponent pressure.
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cd(nx, ny, tx, ty)
        opd = cd(ox, oy, tx, ty)

        # Immediate collection is best; also avoid moves that let opponent have strictly better reach.
        collect = 1.0 if (nx, ny) == (tx, ty) else 0.0
        my_delta = cd(sx, sy, tx, ty) - myd
        opp_pressure = (cd(ox, oy, tx, ty) - opd)

        # Secondary objective: increase distance from opponent when not collecting.
        opp_dist = cd(nx, ny, ox, oy)
        val = (10.0 * collect) + (2.5 * my_delta) + (1.0 * (opd - myd)) + (0.1 * opp_dist) - (0.2 * abs(nx - tx) + 0.2 * abs(ny - ty)) + (0.05 * opp_pressure)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    # If all moves were blocked/invalid, stay.
    return best_move if isinstance(best_move, list) else [0, 0]