def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Territory edge seeking / raid: push into opponent frontier and convert nearby unclaimed.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Basic distances (Manhattan) to bias toward opponent.
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_from_opp = abs(sx - ox) + abs(sy - oy)
        closer = d_from_opp - d_to_opp  # positive if we move toward opponent

        # Frontier value: opponent territory and adjacent unclaimed.
        is_self = (nx, ny) in selfT
        is_opp = (nx, ny) in oppT
        is_uncl = (nx, ny) in unclaimed

        # Count "opponent adjacency" to estimate frontier capture impact.
        adj_opp = 0
        adj_uncl = 0
        for ax, ay in moves:
            px, py = nx + ax, ny + ay
            if not inb(px, py) or (px, py) in obstacles:
                continue
            if (px, py) in oppT:
                adj_opp += 1
            elif (px, py) in unclaimed:
                adj_uncl += 1

        # Avoid getting trapped: penalize moves that reduce room (near obstacles/edges).
        free_n = 0
        for ax, ay in moves:
            px, py = nx + ax, ny + ay
            if inb(px, py) and (px, py) not in obstacles:
                free_n += 1

        score = 0.0
        score += 6.0 * closer
        if is_opp:
            score += 25.0 + 2.0 * adj_opp + 0.5 * adj_uncl
        elif is_uncl:
            score += 10.0 + 1.5 * adj_opp + 0.3 * adj_uncl
        elif is_self:
            score -= 0.5  # less exciting to stay on already-owned cells
        else:
            score += 1.0 * adj_uncl  # move toward border pockets even if unclaimed set is empty

        score += 0.2 * free_n
        # Deterministic tie-break: prefer (dx,dy) closer to (1,1) direction only via ordering below.
        if score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]