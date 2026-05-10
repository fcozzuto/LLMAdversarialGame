def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = None
    best_move = [0, 0]

    # Prefer moves that (a) reduce own distance to a resource, and (b) maximize being earlier than opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
            if nx == sx and ny == sy and (dx, dy) != (0, 0):
                continue

        # Evaluate the best resource from the candidate position.
        # Value: (opponent_advantage, -own_distance, -center_bias, tie by lex)
        best_for_move = None
        for rx, ry in resources:
            if not cell_ok(rx, ry):
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive => we are earlier/closer
            center_bias = -((rx - (w - 1) / 2) ** 2 + (ry - (h - 1) / 2) ** 2)
            # Small extra bias toward collecting a resource immediately
            imm = 1 if sd == 0 else 0
            cand = (adv + 0.01 * imm, -sd + 0.001 * imm, center_bias, -rx, -ry)
            if best_for_move is None or cand > best_for_move:
                best_for_move = cand

        if best_for_move is None:
            continue
        if best_val is None or best_for_move > best_val:
            best_val = best_for_move
            best_move = [nx - sx, ny - sy]

    return [int(best_move[0]), int(best_move[1])]