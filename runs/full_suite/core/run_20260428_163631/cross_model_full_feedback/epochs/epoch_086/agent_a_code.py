def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    op = (ox, oy)

    # Opponent's likely target: closest resource to them
    if resources:
        op_target = min(resources, key=lambda r: man(op, r))
        op_td = man(op, op_target)
    else:
        op_target = None
        op_td = 10**9

    # Evaluate each move by best "take" target plus a deterrent if opponent is too close
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy, nx, ny in legal:
        my2 = (nx, ny)
        if not resources:
            # If no resources, just move away from opponent deterministically
            dist_op = man(my2, op)
            score = dist_op
        else:
            # If opponent is closer to their nearest target than we can match, avoid that race.
            # Prefer resources where we can get there earlier than opponent by margin.
            best_take = -10**18
            for r in resources:
                d_my = man(my2, r)
                d_op = man(op, r)
                margin = d_op - d_my
                # Light preference for nearer resources (reduce dithering)
                tie = -0.01 * d_my
                # If we both chase the same target, discourage when we can't arrive first
                race_pen = 0.0
                if r == op_target and margin <= 0:
                    race_pen = -5.0 * (op_td - d_my + 1)
                val = margin + tie + race_pen
                if val > best_take:
                    best_take = val

            # Deterrent: if opponent is extremely close, prioritize increasing distance a bit
            opp_close = man(my2, op)
            deterrent = 0.3 * (opp_close)

            score = best_take + deterrent

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]