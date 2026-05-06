def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    my_half_bias = ((sx + sy) <= (w - 1 + h - 1) / 2)
    cx, cy = (w - 1) // 2, (h - 1) // 2
    t = observation.get("turn_index", 0)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        my_pos = (nx, ny)
        op_pos = (ox, oy)

        my_closest = min(dist(my_pos, r) for r in resources)
        op_closest = min(dist(op_pos, r) for r in resources)

        # Advantage: resources where we are closer than opponent.
        adv = 0
        weighted_adv = 0
        for r in resources:
            md = dist(my_pos, r)
            od = dist(op_pos, r)
            if md < od:
                d = od - md
                adv += d
                # Bias toward resources on/near our side early to avoid corner-guard traps.
                side = (r[0] + r[1] <= (w - 1 + h - 1) / 2)
                bias = 1.25 if (my_half_bias == side) else 0.85
                weighted_adv += bias * d

        # Center drift as a tie-breaker, helps after early phase.
        center = dist(my_pos, (cx, cy))
        # Safety: avoid moves that let opponent be closer by a lot to the best target.
        op_pressure = 0
        best_od = min(dist(op_pos, r) for r in resources)
        for r in resources:
            if dist(op_pos, r) == best_od:
                op_pressure = min(op_pressure, dist(my_pos, r) - best_od)
        if op_pressure == 0:
            op_pressure = 0

        # Primary: maximize advantage; Secondary: minimize our closest; Tertiary: minimize center distance.
        # Early game favors weighted_adv; later favors raw adv (to catch late switches).
        primary = weighted_adv if t < 30 else adv
        key = (-primary, my_closest, center, - (op_closest - my_closest))
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return best_move