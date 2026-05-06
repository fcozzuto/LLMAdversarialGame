def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Deterministic move order: prefer staying? slightly else.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Strategy: maximize (our advantage to some resource), penalize giving opponent lead,
        # and add small bias to head toward the globally best target.
        v = 0
        near_ours = 10**9
        near_opp = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds < near_ours:
                near_ours = ds
            if do < near_opp:
                near_opp = do

            # Advantage-based: if we're closer, reward more; if opponent closer, punish more.
            # Use reciprocal distance so closer items dominate.
            adv = (do - ds)  # positive means we are closer than opponent
            v += adv * 20 / (1 + ds + do)

            # Strongly discourage stepping into a cell that makes us "worse" for all key nearby resources.
            if do <= ds:
                v -= (ds - do + 1) * 8 / (1 + ds)

        # Additional global structure: keep opponent in mind (intercept if they are very near a resource).
        v += (near_opp - near_ours) * 10 / (1 + near_ours + near_opp)

        # Small tiebreakers: avoid oscillation by preferring moves that change position unless staying is best.
        if dx == 0 and dy == 0:
            v -= 0.5
        # Deterministic tie-breaker based on move coordinates.
        if best is None or v > best_val or (v == best_val and (dx, dy) < best):
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]