def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    my = observation["self_position"]
    op = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def clamp(x, y):
        if x < 0: x = 0
        if y < 0: y = 0
        if x >= w: x = w - 1
        if y >= h: y = h - 1
        return x, y

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return abs(dx) + abs(dy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    my_has_resource = set(tuple(p) for p in resources)

    for dx, dy in moves:
        nx, ny = clamp(my[0] + dx, my[1] + dy)
        if (nx, ny) in obstacles:
            nx, ny = my[0], my[1]
        me_next = (nx, ny)

        # If we can pick a resource now, prioritize it strongly.
        capture = 1 if (nx, ny) in my_has_resource else 0

        # Evaluate by how much this move improves "being closer than opponent" to resources.
        local_best = -10**18
        for rx, ry in my_has_resource:
            if (rx, ry) in obstacles:
                continue
            me_d = dist(me_next, (rx, ry))
            op_d = dist(tuple(op), (rx, ry))
            s = (op_d - me_d) - 0.01 * me_d  # prefer closer when tie
            if me_d == 0:
                s += 5.0
            if s > local_best:
                local_best = s

        # Mildly prefer staying away from the opponent unless it helps contesting resources.
        op_d_next = dist(me_next, tuple(op))
        score = capture * 1000.0 + local_best + 0.02 * op_d_next

        if score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score:
            # Deterministic tie-break: prefer moves with smaller index order already; keep existing.
            pass

    return best if best is not None else [0, 0]