def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    t = int(observation.get("turn_index") or 0)
    rem = int(observation.get("remaining_resource_count") or 0)
    late = 1 if (t > 46 or rem <= 5) else 0

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_adv = -10**18
    if resources:
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = (od - myd)  # positive => we are closer
            # Late game: prioritize shortest actual path once things are tight
            if late:
                adv = adv + (-(myd) * 0.6) + (0.2 * od)
            # Small tie-break: prefer targets that are more "toward us" than opponent (by quadrant)
            adv = adv + 0.05 * ( (abs(rx - sx) + abs(ry - sy)) * -1 + (abs(rx - ox) + abs(ry - oy)) * 1 )
            if adv > best_adv:
                best_adv = adv
                best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best

    # Choose move that maximizes contest: get closer to target while (slightly) making it harder for opponent
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        # Our value: advantage improvement, then closer distance
        val = (od2 - myd2)
        val = val * 1000 - myd2
        # Obstacle-aware: discourage staying if already can improve
        if dx == 0 and dy == 0:
            val -= 0.2
        # Prefer moves that do not walk directly toward opponent when we are already winning
        if best_adv > 0:
            val -= 0.05 * man(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]