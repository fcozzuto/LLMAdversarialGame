def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        # Row-control: if opponent is sweeping a row, mirror with vertical alignment first.
        best = [0, 0]
        bestv = 10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            v = abs(ny - oy)
            if v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Strategy: pick the move that creates the largest lead over the opponent on a single best contest resource.
    # Also add a small row-parity/row-alignment bias to fight row-sweep behavior.
    best_move = [0, 0]
    best_score = -10**18
    opp_row = oy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue

        row_bias = -abs(ny - opp_row) * 0.3  # align with opponent's sweep row
        parity_bias = -((ny + nx) & 1) * 0.01  # tiny deterministic tie-break

        # Best contest target: maximize (opp_dist - my_dist) with tighter preference for reachable resources.
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)
            # If we're closer, reward by the gap; if not, penalize but still consider.
            gap = oppd - myd
            # Prefer resources we can reach quickly in general.
            reach = -0.15 * myd
            score = gap * 2.2 + reach
            if score > local_best:
                local_best = score

        score_total = local_best + row_bias + parity_bias
        if score_total > best_score:
            best_score = score_total
            best_move = [dx, dy]

    return best_move