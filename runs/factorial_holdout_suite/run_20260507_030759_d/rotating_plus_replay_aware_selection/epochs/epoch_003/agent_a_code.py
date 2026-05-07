def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_toward(s, t):
        dx = t[0] - s[0]
        dy = t[1] - s[1]
        if dx > 0: mdx = 1
        elif dx < 0: mdx = -1
        else: mdx = 0
        if dy > 0: mdy = 1
        elif dy < 0: mdy = -1
        else: mdy = 0
        return mdx, mdy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist_cheb((nx, ny), (cx, cy))
            if best is None or d < best[0] or (d == best[0] and (nx, ny) < best[1]):
                best = (d, (nx, ny))
        return [best[1][0] - sx, best[1][1] - sy] if best else [0, 0]

    # Choose a target where we are more likely to arrive earlier than opponent.
    best_target = None
    best_key = None
    for rx, ry in resources:
        our_d = dist_cheb((sx, sy), (rx, ry))
        opp_d = dist_cheb((ox, oy), (rx, ry))
        lead = our_d - opp_d  # smaller is better
        # small tie-breakers: prefer resources nearer to us and avoid giving opponent immediate access via same sweep row
        row_bias = 0 if ry != oy else 0.25
        key = (lead + row_bias, our_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    preferred = set()
    mdx, mdy = step_toward((sx, sy), (tx, ty))
    for dx, dy in moves:
        if inb(sx + dx, sy + dy):
            preferred.add((dx, dy))

    # Evaluate each legal next move by: (1) improved lead to target, (2) avoid stepping into dead-ends vs obstacles.
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        our_next = dist_cheb((nx, ny), (tx, ty))
        opp_d = dist_cheb((ox, oy), (tx, ty))
        lead_next = our_next - opp_d
        # obstacle pressure: count legal neighbors to keep mobility
        mob = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay):
                mob += 1
        # sweep counter: if opponent is aligned in row, bias toward changing row (diagonal/horizontal)
        row_align = 1 if ny == oy else 0
        score = (lead_next, our_next, -mob, row_align, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move else [0, 0]