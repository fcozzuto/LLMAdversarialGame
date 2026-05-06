def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def man(nx, ny, tx, ty):
        return abs(tx - nx) + abs(ty - ny)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = 0 if ox == x else (1 if ox > x else -1)
        dy = 0 if oy == y else (1 if oy > y else -1)
        return [-dx, -dy]

    # Pick move using one-step lookahead: best next position for controlling the most "winnable" resource.
    # Resource desirability is higher if opponent is farther than we are (lead), with a slight preference for closeness.
    def res_score(tx, ty):
        d_me = man(x, y, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        return (d_opp - d_me) * 1000 - d_me

    # Choose top few resources deterministically.
    scored = [(res_score(r[0], r[1]), r[0], r[1]) for r in resources]
    scored.sort(key=lambda t: (-t[0], t[1], t[2]))
    top = scored[:3]

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue

        # For each candidate resource, compute immediate control value after moving.
        move_val = None
        for _, tx, ty in top:
            d_me2 = man(nx, ny, tx, ty)
            d_opp2 = man(ox, oy, tx, ty)
            v = (d_opp2 - d_me2) * 1000 - d_me2
            # If we can capture immediately, heavily prioritize.
            if nx == tx and ny == ty:
                v += 1_000_000
            if move_val is None or v > move_val:
                move_val = v
        # Tie-break deterministically: prefer lower self-distance to the chosen top resource, then lexicographic move.
        _, tx0, ty0 = top[0]
        tie_self = man(nx, ny, tx0, ty0)
        cand = (move_val, -tie_self, -dx, -dy)
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]