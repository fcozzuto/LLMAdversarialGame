def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_key = None
    best_move = (0, 0)

    # Predict opponent's likely next target: the closest resource to them (ties by lexicographic).
    opp_target = None
    best_od = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        key = (d, rx, ry)
        if best_od is None or key < best_od:
            best_od = key
            opp_target = (rx, ry)

    tx, ty = opp_target
    my_turn = int(observation.get("turn_index", 0))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # Core: maximize advantage vs opponent on likely target; then secure other resources.
        my_dt = cheb(nx, ny, tx, ty)
        odt = cheb(ox, oy, tx, ty)
        adv = odt - my_dt  # positive means I'm closer on the target

        nearest_my = None
        nearest_opp = None
        for rx, ry in resources:
            dmy = cheb(nx, ny, rx, ry)
            if nearest_my is None or dmy < nearest_my:
                nearest_my = dmy
            dop = cheb(ox, oy, rx, ry)
            if nearest_opp is None or dop < nearest_opp:
                nearest_opp = dop

        # If we can't beat their target soon, move toward a resource that most increases relative advantage.
        rel_gain = 0
        if adv < 0:
            for rx, ry in resources:
                g = cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)
                if g > rel_gain:
                    rel_gain = g

        # Small deterministic bias to reduce oscillation: prefer directions that progress on parity.
        parity_bias = -abs((nx + ny + my_turn) % 2 - 0)

        key = (-(adv + (rel_gain if adv < 0 else 0)), nearest_my if nearest_my is not None else 10**9, -parity_bias, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]