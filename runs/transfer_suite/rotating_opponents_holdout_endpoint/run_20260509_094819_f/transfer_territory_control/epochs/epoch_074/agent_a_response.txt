def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []) if x is not None)
    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target selection: prioritize nearest unclaimed; else chase opponent border/territory; else head to center.
    if unclaimed:
        candidates = list(unclaimed)
    elif opp_t:
        candidates = list(opp_t)
    else:
        cx, cy = (w // 2), (h // 2)
        candidates = [(cx, cy)]

    # Deterministic tie-break by (distance, x, y)
    tx, ty = min(candidates, key=lambda c: (man((sx, sy), c), c[0], c[1]))

    # Slight preference to keep pressure toward opponent's side.
    bias_x = 1 if ox > sx else (-1 if ox < sx else 0)
    bias_y = 1 if oy > sy else (-1 if oy < sy else 0)

    best_move = (0, 0)
    best_cost = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_target = man((nx, ny), (tx, ty))
        d_opp = man((nx, ny), (ox, oy))

        # Territory interaction heuristics:
        # - entering opponent territory is good (flip control)
        # - entering unclaimed is good for expansion
        # - avoid getting stuck by not overshooting far away from opponent when we have no unclaimed
        in_opp = (nx, ny) in opp_t
        in_unclaimed = (nx, ny) in unclaimed
        in_self = (nx, ny) in self_t

        # Encourage edge control by preferring moves that reduce distance to nearest target
        cost = 10 * d_target + 2 * d_opp

        if in_unclaimed:
            cost -= 6
        if in_opp:
            cost -= 12
        if in_self and (not in_unclaimed) and (not in_opp):
            cost += 2

        # Small directional bias toward opponent to keep pressure.
        cost -= 0.5 * (dx * bias_x + dy * bias_y)

        # Deterministic tie-break: prefer lexicographically smallest move among equals
        if cost < best_cost or (cost == best_cost and (dx, dy) < best_move):
            best_cost = cost
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]