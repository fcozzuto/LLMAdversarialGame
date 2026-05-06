def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_val = None

    # "Interceptor/blocker" heuristic:
    # Prefer moves that (1) improve advantage on the closest contested resource,
    # (2) let us become the closer agent to more resources overall,
    # (3) while not walking into obstacles / off-grid.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_d_self = []
        opp_d_self = []
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            my = cheb(nx, ny, rx, ry)
            op = cheb(ox, oy, rx, ry)
            my_d_self.append((my, op, rx, ry))

        if not my_d_self:
            continue

        # Closest contested resource: where opponent is closer or about equal.
        contested = min(my_d_self, key=lambda t: (t[1] - t[0], t[0]))
        my_c, op_c, rx_c, ry_c = contested

        # Overall blocking potential: count resources where we can be closer than opponent after this move.
        block = 0
        # Also encourage moving towards resources in opponent's sweep lanes (row/col alignment).
        align = 0
        for my, op, rx, ry in my_d_self:
            if my < op:
                block += 1
            # Opponent sweep_rows: penalize letting opponent keep same-row access; reward moving into their row/col influence.
            if ry == oy or rx == ox:
                align += 1 if cheb(nx, ny, rx, ry) < cheb(sx, sy, rx, ry) else 0

        # Main score: maximize (opponent distance - my distance) on the contested resource,
        # then maximize block, then align, then prefer closer to contested.
        val = (op_c - my_c, block, align, -my_c, -cheb(nx, ny, ox, oy), dx * 0 + dy * 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move