def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx if inside(sx + dx, sy) else 0, dy if inside(sx, sy + dy) else 0]

    # Targeting: fight sweep-by-row using opponent's current y first; otherwise nearest resource.
    opp_row = oy
    row_resources = [p for p in resources if p[1] == opp_row]
    if row_resources:
        # Choose resource on opponent row that we can reach reasonably and that isn't already closer to opponent.
        best = None
        best_s = None
        for rx, ry in row_resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            s = ds + (0 if do >= ds else 6) + (0 if (rx - ox) * (1 if sx > ox else -1) <= 0 else 2)
            if best is None or s < best_s:
                best, best_s = (rx, ry), s
        tx, ty = best
    else:
        tx, ty = min(resources, key=lambda p: man(sx, sy, p[0], p[1]))

    # Move selection: reduce our distance, while increasing opponent's distance-to-target (contest resources).
    best_move = None
    best_cost = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_d = man(nx, ny, tx, ty)
        op_d = man(ox, oy, tx, ty)
        # Encourage moving to target row if opponent is sweeping.
        row_bonus = -1 if ny == opp_row else 0
        # Mild discouragement for staying put when we can improve.
        stay_pen = 1 if dx == 0 and dy == 0 else 0
        cost = my_d * 10 - op_d * 3 + row_bonus + stay_pen
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]