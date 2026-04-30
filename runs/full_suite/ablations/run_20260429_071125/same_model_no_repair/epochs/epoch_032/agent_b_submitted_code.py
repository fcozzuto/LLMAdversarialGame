def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best_val = None
    best_move = (0, 0)

    def neighbor_block_penalty(nx, ny):
        # Encourage routes that aren't immediately adjacent to obstacles.
        p = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            x, y = nx + dx, ny + dy
            if (x, y) in occ:
                p += 0.35
        return p

    if not resources:
        # Deterministic fallback: move toward center while avoiding obstacle cells.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                nx, ny = sx, sy
                dx, dy = 0, 0
            val = -cheb(nx, ny, cx, cy) + 0.03 * cheb(nx, ny, ox, oy) - neighbor_block_penalty(nx, ny)
            key = (val, -cheb(nx, ny, ox, oy), dx, dy)
            if best_val is None or key > best_val:
                best_val, best_move = key, (dx, dy)
        return [best_move[0], best_move[1]]

    # Score each candidate by the best "race" resource we can reach relatively sooner than opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Find opponent's nearest resource (for tactical focus).
        opp_near = 10**9
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            if d < opp_near:
                opp_near = d

        best_race = -10**9
        best_r_my = 10**9
        best_r_op = 10**9

        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Primary: maximize how much earlier we can be.
            race = (op_d - my_d) * 12
            # Secondary: prefer globally close targets (even if tie in race).
            race -= 0.9 * my_d
            # Tactical: slightly emphasize resources that are also near opponent.
            if op_d <= opp_near:
                race += 2.2
            if race > best_race or (race == best_race and (my_d < best_r_my or (my_d == best_r_my and op_d < best_r_op))):
                best_race = race