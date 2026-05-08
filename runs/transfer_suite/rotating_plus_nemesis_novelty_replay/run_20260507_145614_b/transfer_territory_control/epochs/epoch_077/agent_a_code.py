def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    opp_set = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opp_set.add((x, y))

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    def edge_bias(x, y):
        return (1 if x in (0, w - 1) else 0) + (1 if y in (0, h - 1) else 0)

    def adj_opp(x, y):
        c = 0
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in opp_set:
                c += 1
        return c

    # Choose a target deterministically: adjacent-to-opponent unclaimed first, else any unclaimed, else stay.
    target = None
    best = None
    if unclaimed:
        for x, y in unclaimed:
            a = adj_opp(x, y)
            # Prefer edge cells, then frontier (adjacent to opp), but also avoid going too close to opponent center.
            # Deterministic tie-break via coordinate ordering.
            dist_to_opp = abs(x - ox) + abs(y - oy)
            score = (-2 * a, -edge_bias(x, y), dist_to_opp, abs(x - sx) + abs(y - sy), x, y)
            if best is None or score < best:
                best = score
                target = (x, y)

    if target is None:
        return [0, 0]

    tx, ty = target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # If stepping into opponent territory, flipping is enabled; we only bias toward it slightly.
        step_into_opp = 1 if (nx, ny) in opp_set else 0
        key = (
            0 if (nx, ny) in unclaimed else 1,  # prefer taking/claiming unclaimed
            -step_into_opp,
            abs(nx - tx) + abs(ny - ty),
            -(abs(nx - ox) + abs(ny - oy)),  # prefer not being too close to opponent
            dx, dy
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]