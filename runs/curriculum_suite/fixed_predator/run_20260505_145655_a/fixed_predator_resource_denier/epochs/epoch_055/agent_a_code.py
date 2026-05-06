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
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Select a resource to "deny": we prefer cells where opponent is farther than us (so we can reach first),
    # while still keeping pressure by choosing high opp-self distance advantage.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Higher means better denial target; also prefer closer targets to avoid slow wandering.
        score = (od - sd) * 8 - sd * 0.6
        # Small center bias to reduce oscillations.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -(((rx - cx) * (rx - cx)) + ((ry - cy) * (ry - cy))) * 1e-4
        t = (score + center_bias, -sd, -od, rx, ry)
        if best is None or t > best:
            best = t
    tx, ty = best[3], best[4]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate immediate next step: maximize denial outcome vs opponent for the chosen target,
    # while avoiding stepping into obstacles and improving move quality.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        # Prefer being closer to target than opponent, and closer overall.
        deny = (od2 - sd2) * 10 - sd2
        # Slightly prefer moves that reduce distance to target and don't hug obstacles.
        neigh_block = 0
        for a, b in moves:
            px, py = nx + a, ny + b
            if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                neigh_block += 1
        t = (deny - neigh_block * 0.25, -sd2, dx, dy)
        if best_move is None or t > best_move:
            best_move = t

    if best_move is None:
        return [0, 0]

    # Extract dx,dy from best_move tuple: (score, -sd2, dx, dy)
    return [int(best_move[2]), int(best_move[3])]