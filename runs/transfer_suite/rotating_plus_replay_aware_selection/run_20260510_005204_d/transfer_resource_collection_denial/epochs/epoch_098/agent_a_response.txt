def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)
    rem_cnt = observation.get("remaining_resource_count", len(resources))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    # Move ordering fixed for determinism.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Late game: more greedy for nearest resource; early: emphasize winning races vs opponent.
    late = 1.0 if turns_remaining <= 10 else 0.0
    race_weight = 1.8 * (1.0 - late) + 0.6 * late
    greedy_weight = 1.2 * late + 0.3 * (1.0 - late)

    best = None
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate best resource for this next position.
        sc = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)

            # Encourage picking resources we can reach first.
            race = (d_opp - d_self)
            # Encourage shorter distance even if opponent is also close.
            greedy = -d_self

            # Small bias toward resource "value" via remaining count (more resources => less commitment).
            commit = 0.15 * (1.0 - min(1.0, rem_cnt / 12.0)) * (1 if d_self == 0 else 0)

            local = race_weight * race + greedy_weight * greedy + commit
            if local > sc:
                sc = local

        # Prefer immediate pickup if possible.
        if sc > best_sc or (sc == best_sc and best is not None and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]