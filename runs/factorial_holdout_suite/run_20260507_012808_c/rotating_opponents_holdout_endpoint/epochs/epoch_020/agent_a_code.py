def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a target resource that we can reach before (or at least no worse than) opponent.
    # Tie-break: prefer larger advantage and closer distance.
    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        adv = od - sd  # positive means we are closer or can get there first
        key = (-(adv + 0.001 * (tx + ty)), sd)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    moves.append((0, 0))

    # Score moves: reduce our distance to target, avoid letting opponent get closer to same target.
    # Slightly encourage movement that also moves away from nearest obstacle-adjacent cell.
    def near_obst_score(x, y):
        # Count obstacle neighbors; discourage stepping adjacent/onto near cluster.
        cnt = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    cnt += 1
        return cnt

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)

        # Prefer improving advantage; penalize losing it.
        adv2 = od2 - sd2
        # Small bias to progress toward target to break ties.
        prog = -(abs(nx - tx) + abs(ny - ty))

        val = (-adv2, sd2, -prog, near_obst_score(nx, ny))
        # Convert to comparable single direction: we already used negative for some parts; keep lexicographic order.
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]