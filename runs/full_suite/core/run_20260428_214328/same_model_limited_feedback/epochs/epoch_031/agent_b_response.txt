def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        # No resources visible: move to maximize distance from opponent while staying safe.
        best = (None, -10**9)
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d > best[1]:
                best = ((dx, dy), d)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    def mindist(px, py):
        md = 10**9
        for rx, ry in resources:
            d = abs(px - rx) + abs(py - ry)
            if d < md:
                md = d
        return md

    # Prefer moves that reduce distance to the nearest resource; also avoid being too close to opponent.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_md = mindist(nx, ny)
        opp_md = mindist(ox, oy)

        my_opp = abs(nx - ox) + abs(ny - oy)

        # Bonus if we could land on a resource.
        on_resource = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0

        # Obstacle proximity penalty (soft).
        prox_pen = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if (ax, ay) in obstacles:
                    prox_pen += 1

        # Score: primary minimize distance to resources; secondary increase separation from opponent.
        # Deterministic tie-breaking comes from fixed delta order.
        score = (-my_md) + 2.5 * on_resource + 0.06 * my_opp - 0.12 * prox_pen + 0.02 * (opp_md - my_md)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]