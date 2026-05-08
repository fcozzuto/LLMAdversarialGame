def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Intercept: target unclaimed cells adjacent to opponent territory (block edge expansion).
    targets = []
    for (x, y) in opp_terr:
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                targets.append((nx, ny))
    # Fallback: head to nearest unclaimed cell that is not near obstacles (reduce being boxed in).
    if not targets:
        targets = list(unclaimed)

    best_move = (0, 0)
    best_val = -10**18

    def obstacle_proximity(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in obstacles:
                c += 1
        return c

    # Simple determinism: tie-break by lexicographic move.
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Immediate value
        val = 0
        if (nx, ny) in self_terr:
            val += 2
        elif (nx, ny) in unclaimed:
            val += 10
        elif (nx, ny) in opp_terr:
            val += 6  # flipping helps even if lower than unclaimed

        val -= 2 * obstacle_proximity(nx, ny)

        # Choose best intercept target for this move (min distance with priority for intercept blockers).
        if targets:
            # Compute closest target distance; deterministic min.
            md = 10**9
            for tx, ty in targets:
                d = abs(tx - nx) + abs(ty - ny)
                if d < md:
                    md = d
            val -= md

        # If we are closer to opponent than we were, slight bonus (pressure back).
        if (abs(nx - sy) + abs(ny - (w - 1))) > 10**8:
            pass
        # More robust: compare distance to opponent position directly.
        op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
        ox, oy = int(op[0]), int(op[1])
        d_self = abs(sx - ox) + abs(sy - oy)
        d_new = abs(nx - ox) + abs(ny - oy)
        if d_new < d_self:
            val += 3
        elif d_new > d_self:
            val -= 1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]