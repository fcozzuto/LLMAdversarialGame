def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    resources = [r for r in resources if r not in obstacles]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Heuristic: prioritize resources we can plausibly reach first (or nearly),
    # and break ties by maximizing (opponent_distance - self_distance).
    scored = []
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # If opponent is winning, only take it if we are close enough to contest.
        contest = (sd <= od + 1)
        # Small tie-break to avoid wandering: prefer smaller sd, then larger advantage.
        adv = od - sd
        scored.append((0 if contest else 1, sd, -adv, (tx + ty) % 7, tx, ty, sd, od))

    _, _, _, _, tx, ty, sd, od = min(scored)
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Also consider a slight detour to avoid obvious immediate traps:
    # if moving directly is blocked, try best alternative among 8 directions + stay.
    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (-dx, -dy), (0, 0)]
    best = [0, 0]
    best_key = None
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nsd = man(nx, ny, tx, ty)
            nod = man(nx, ny, ox, oy)  # discourage drifting towards opponent
            # Prefer reducing distance to target, then staying farther from opponent.
            key = (nsd, nod, abs(ox - nx) + abs(oy - ny), (ddx, ddy))
            if best_key is None or key < best_key:
                best_key = key
                best = [ddx, ddy]
    return best