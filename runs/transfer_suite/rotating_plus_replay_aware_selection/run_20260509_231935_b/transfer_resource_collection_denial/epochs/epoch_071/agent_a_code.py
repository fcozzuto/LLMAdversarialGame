def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    res_list = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    resources = [(p[0], p[1]) for p in res_list if p and len(p) >= 2]
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in obs_list if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    dirs = moves

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        oy_pen = 0
        # Prefer taking resources in different row than opponent's current row (counter sweep_rows).
        # If opponent is already on that row, reduce attractiveness.
        # Use absolute row distance to scale.
        for rx, ry in resources:
            my_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            row_block = 3 if ry == oy else 0
            row_far = abs(ry - oy)
            # Prefer winning race: (opp_d - my_d). Also prefer resources that move us closer along with row separation.
            val = (opp_d - my_d) * 12 + (5 if my_d == 0 else 0) + row_far - row_block - (my_d * 0.2)
            # Slight deterministic tie-break: prefer lower (x,y) when equal
            val += -0.000001 * (rx * 8 + ry)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move