def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = set(tuple(r) for r in resources)

    # Predict opponent's next target as their nearest resource.
    best_opp = None
    best_opp_key = None
    for rx, ry in resources:
        od = dist(ox, oy, rx, ry)
        key = (od, rx, ry)
        if best_opp_key is None or key < best_opp_key:
            best_opp_key = key
            best_opp = (rx, ry)
    tx, ty = best_opp

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        my_to_tx = dist(nx, ny, tx, ty)
        op_to_tx = dist(ox, oy, tx, ty)  # opponent target distance now (deterministic baseline)
        slack = op_to_tx - my_to_tx

        # Big reward for picking up a resource this turn.
        pickup = 1 if (nx, ny) in res_set else 0

        # Small tie-breakers: don't walk away; avoid wasting steps by aiming toward target.
        toward = -my_to_tx
        # Also consider if another resource becomes immediately reachable.
        adj_other = 0
        for ex in (nx,):
            pass
        for rx, ry in resources:
            if dist(nx, ny, rx, ry) == 0:
                adj_other = 1
                break

        val = (pickup * 10_000) + (adj_other * 2) + (slack * 50) + (toward)
        key = (-val, dx, dy)  # deterministic min key

        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]