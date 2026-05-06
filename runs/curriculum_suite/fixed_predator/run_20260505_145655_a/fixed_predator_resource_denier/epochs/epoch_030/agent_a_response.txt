def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose a global target that we can reach no slower than opponent; fallback to closest advantage.
    best_target = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        adv = (od - sd) * 10 - sd
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    tx, ty = best_target

    # If opponent is already closer to that target, try to "deny" by moving toward the midpoint corridor.
    # Deterministic corridor target: steer toward the cell on the line with maximal distance reduction for opponent.
    corridor = None
    if dist(sx, sy, tx, ty) > dist(ox, oy, tx, ty):
        midx = (tx + sx) // 2
        midy = (ty + sy) // 2
        corridor = (midx, midy)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Main objective: maximize future advantage on best contestable resource.
        local = -10**18
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Favor being closer and also reduce opponent's potential next reach.
            val = (od - sd) * 12 - sd
            if od <= sd:
                val += 30  # contestable
            # Small tie-break toward resources near our current global target.
            val -= dist(rx, ry, tx, ty) * 0.1
            if val > local:
                local = val

        # Denial / interceptor shaping: reduce opponent advantage by approaching cells that increase their distance to our target.
        deny = 0
        if corridor is not None:
            cx, cy = corridor
            if in_bounds(cx, cy) and (cx, cy) not in obstacles:
                deny = (dist(ox, oy, cx, cy) - dist(nx, ny, cx, cy)) * 3
        else:
            deny = (dist(ox, oy, tx, ty) - dist(nx, ny, tx, ty)) * 2

        val = local + deny

        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer smaller absolute move then lex order.
            def key(m):
                return (abs(m[0]) + abs(m[1]), m[0], m[1])
            if key((dx, dy)) < key(best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]