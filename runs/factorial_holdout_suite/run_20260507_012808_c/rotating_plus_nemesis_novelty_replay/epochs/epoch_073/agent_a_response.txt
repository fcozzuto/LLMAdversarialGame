def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    # Precompute nearest resource distances for current positions
    my_best_d = 10**9
    op_best_d = 10**9
    for rx, ry in resources:
        my_best_d = min(my_best_d, man(sx, sy, rx, ry))
        op_best_d = min(op_best_d, man(ox, oy, rx, ry))

    # Evaluate each move: go to good resources and avoid letting opponent "win races"
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Nearest resource after move
        my_d = 10**9
        for rx, ry in resources:
            my_d = min(my_d, man(nx, ny, rx, ry))

        # Opponent race pressure: how much farther they are from their nearest resource
        # (Higher is better for us). Also slightly reward moves that bring us closer
        # to where we would intercept: resources that are currently competitive.
        op_d = op_best_d
        # Approx "intercept": estimate whether we move toward resources that are near us
        # but also near opponent (contested).
        cont = 0
        for rx, ry in resources:
            if man(ox, oy, rx, ry) <= op_best_d + 1:
                cont += 1 if man(nx, ny, rx, ry) <= my_d + 1 else 0

        score = 0
        score += (my_best_d - my_d) * 12  # faster collection
        score += (op_d - my_best_d) * 2   # indirectly (usually constant)
        score += (op_d - (op_d))  # keep deterministic no-op term

        # Contested resources: increase when we are also close to them
        score += cont * 3
        # Slight preference to reduce own distance to nearest resource
        score -= my_d * 1

        # Tie-break: prefer diagonal progress toward center-right if opponent is there
        center_bias_x = (nx - (w // 2))
        center_bias_y = (ny - (h // 2))
        score += (center_bias_x + center_bias_y) * 0.01

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]