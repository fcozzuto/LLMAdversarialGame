def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    rem = observation.get("remaining_resource_count", len(resources))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_bias = 0.15 if rem > 0 else 0.0

    best_mv = (0, 0)
    best_val = None

    # Pre-sort resources deterministically for tie-breaking
    res_list = sorted((tuple(r) for r in resources), key=lambda p: (p[0], p[1]))
    if not res_list:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep us; treat as such
        # Find nearest resource to take after move, preferring ones opponent isn't closer to
        min_my = 10**9
        min_opp = 10**9
        # Use two-stage evaluation: choose resource minimizing (my_dist - opp_dist*opp_bias)
        local = 10**18
        for rx, ry in res_list:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            v = d_my - opp_bias * d_op
            if v < local:
                local = v
                min_my = d_my
                min_opp = d_op
        d_op_after = cheb(nx, ny, ox, oy)
        # Higher is better: prioritize decreasing my distance and increasing separation
        val = -(min_my) + 0.02 * d_op_after + 0.01 * (min_opp - min_my)
        if best_val is None or val > best_val + 1e-12:
            best_val = val
            best_mv = (dx, dy)
        elif abs(val - best_val) <= 1e-12:
            # Deterministic tie-break
            if moves.index((dx, dy)) < moves.index(best_mv):
                best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]