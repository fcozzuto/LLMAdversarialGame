def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def dist(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = 0, 0
        if sx + sy > (W + H - 2) / 2: tx, ty = W - 1, H - 1
        if ox < W // 2: tx = W - 1
        if oy < H // 2: ty = H - 1
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs: 
                continue
            d = dist(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, dx, dy)
        if best[1] != 0 or best[2] != 0:
            return [int(best[1]), int(best[2])]
        return [0, 0]

    # Evaluate each candidate next position by the best "advantage" it can secure.
    # Advantage for a resource: op_d - my_d (bigger means we arrive sooner).
    best_move = None
    best_val = None
    tie = None

    # Secondary heuristic: when contested, move to maximize reduction in distance to the most valuable
    # resource (tie-break by closeness to our position and being safer vs opponent).
    def res_value(rx, ry):
        # Prefer resources not too close to opponent and not too far overall.
        # Deterministic, no need for full search.
        return (dist(rx, ry, 0, 0) % 7) + (dist(rx, ry, W - 1, H - 1) % 5)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_adv = -10**9
        best_rxry = None
        best_res_key = None
        for rx, ry in resources:
            my_d = dist(nx, ny, rx, ry)
            op_d = dist(ox, oy, rx, ry)
            adv = op_d - my_d
            # Tie-break: choose higher value and smaller my distance
            key = (-adv, res_value(rx, ry), my_d)
            if best_res_key is None or key < best_res_key:
                best_res_key = key
                best_adv = adv
                best_rxry = (rx, ry)

        # If we can secure a resource (positive advantage), maximize it.
        # Otherwise, still try to reduce opponent's lead: maximize (adv) but with strong pressure.
        # Add slight preference for staying closer to chosen target.
        if best_rxry is None:
            continue
        rx, ry = best_rxry
        my_d_next = dist(nx, ny, rx, ry)
        # Value for sorting moves:
        # - First: best_adv descending (prefer we arrive sooner)
        # - Second: my_d_next ascending
        # - Third: deterministic preference ordering by dx,dy
        val = (-(best_adv), my_d_next, dx, dy)
        if best_move is None or val < best_val:
            best_move = (dx, dy)
            best_val = val
            tie = best_rxry

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]