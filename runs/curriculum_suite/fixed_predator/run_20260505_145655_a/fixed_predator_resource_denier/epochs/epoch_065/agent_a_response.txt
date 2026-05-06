def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    # Choose a target resource to deny, biased toward those the opponent can reach sooner.
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_rx, best_ry = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        denial = (od - sd)  # positive means we're closer than opponent; prefer large opponent advantage instead
        # We want opponent to be closer to what we go deny: maximize (sd - od) primarily, then closeness.
        key = (-(sd - od), sd, (rx - (w - 1) / 2.0) ** 2 + (ry - (h - 1) / 2.0) ** 2, -od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry

    # Consider moves; avoid stepping into obstacles/outside. Prefer cells that reduce distance to target
    # while also increasing distance from opponent (deny/block).
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Small deterministic diversification by turn parity to avoid stagnation.
    parity = int(observation.get("turn_index", 0)) & 1

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # If we can get to the target before opponent, that still wins; otherwise, block by staying between.
        # Also reward stepping toward opponent if it would allow interception (closer to opponent than we are).
        to_opp = man(nx, ny, ox, oy)

        # "Between" bias: minimize sum of distances to ourselves->target and opponent->target.
        between = abs((man(sx, sy, tx, ty) - sd) - (od - man(ox, oy, tx, ty)))  # mostly zero, but deterministic
        # Additional: prefer moving to cells that keep opponent farther from target relative to us.
        rel = (od - sd)

        val = (sd, -rel, to_opp, (nx + ny + parity) * 1e-6, between)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move