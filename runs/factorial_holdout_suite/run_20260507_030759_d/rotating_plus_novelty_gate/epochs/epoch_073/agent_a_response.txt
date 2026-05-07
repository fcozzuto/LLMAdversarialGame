def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((p[0], p[1]))
    if (sx, sy) in set(resources):
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))

    if not legal or not resources:
        return [0, 0]

    my = (sx, sy)
    op = (ox, oy)

    # Opponent is nearest-resource; estimate their likely target.
    opp_best = None
    best_do = None
    for r in resources:
        do = dist(op, r)
        if best_do is None or do < best_do or (do == best_do and (r[0], r[1]) < opp_best):
            best_do = do
            opp_best = r

    # Choose a target where we are at least as competitive as the opponent.
    best_target = None
    best_key = None
    for r in resources:
        dm = dist(my, r)
        do = dist(op, r)
        # Primary: we want dm <= do; secondary: maximize margin (do-dm)
        # Tertiary: avoid likely opponent target if similarly competitive.
        is_opp = 1 if r == opp_best else 0
        key = (0 if dm <= do else 1, dm - do, is_opp, dm, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_target = r

    tx, ty = best_target
    # Pick move that most improves our relative standing on the chosen target,
    # while gently discouraging stepping into squares that give the opponent more advantage.
    best_move = (0, 0)
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dm1 = abs(nx - tx) + abs(ny - ty)
        do1 = abs(ox - tx) + abs(oy - ty)
        # If we collect next, do it.
        collect_bonus = 0
        if (nx, ny) in resources:
            collect_bonus = -1000000
        # Score: prioritize smaller dm1, then larger (do1 - dm1), deterministic tie-break by position.
        score = (collect_bonus, dm1, -(do1 - dm1), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]