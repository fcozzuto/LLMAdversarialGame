def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    # Our closest and opponent's closest
    our_best = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
    opp_best = min(resources, key=lambda r: man(ox, oy, r[0], r[1]))
    d_our = man(sx, sy, our_best[0], our_best[1])
    d_opp = man(ox, oy, opp_best[0], opp_best[1])

    # If we're behind, opportunistically switch to a resource we can reach earlier than opponent
    best_target = None
    if d_our > d_opp:
        # Choose deterministic highest advantage among reachable-befores
        candidates = []
        for rx, ry in resources:
            a = man(sx, sy, rx, ry)
            b = man(ox, oy, rx, ry)
            adv = b - a
            if adv > 0:
                candidates.append((adv, a, rx, ry))
        if candidates:
            candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
            best_target = (candidates[0][2], candidates[0][3])
        else:
            best_target = our_best
    else:
        best_target = our_best

    tx, ty = best_target
    dx, dy = sign(tx - sx), sign(ty - sy)

    # If direct step hits obstacle, try alternate deterministic local moves
    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0),
             (sign(tx - sx), sign(ty - sy)), (-sign(tx - sx), sign(ty - sy)),
             (sign(tx - sx), -sign(ty - sy))]
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]

    # Fallback: stay
    return [0, 0]