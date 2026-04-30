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
    adj = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If no resources, just head to center while avoiding obstacles
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            near = 0
            for ax, ay in adj:
                if (nx + ax, ny + ay) in occ:
                    near += 1
            v = -cheb(nx, ny, tx, ty) - 2.0 * near
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Predict opponent greedy response (toward best resource for them)
    def opp_next_dist_to_best(rx, ry):
        d = cheb(ox, oy, rx, ry)
        return 0 if d <= 1 else d - 1  # king can reduce cheb by 1 per move

    # Precompute for speed
    opp_best_for = []
    for rx, ry in resources:
        opp_best_for.append(opp_next_dist_to_best(rx, ry))

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # Obstacle risk: heavy penalty near obstacles
        near = 0
        for ax, ay in adj:
            if inb(nx + ax, ny + ay) and (nx + ax, ny + ay) in occ:
                near += 1
        risk = -6.0 * near

        # Evaluate competition over nearest resource after our move vs opponent's predicted next
        my_best_win = -10**18
        for i, (rx, ry) in enumerate(resources):
            myd = cheb(nx, ny, rx, ry)
            my_next = 0 if myd == 0 else myd  # we score by current reachability after this move
            od_next = opp_best_for[i]

            # If we can take immediately
            if myd == 0:
                win = 2000000.0
            else:
                # Prefer being closer than opponent after one move
                margin = od_next - my_next
                # Also mildly prefer making progress (smaller myd)
                win = 1200.0 * margin - 3.0 * myd

                # If opponent is already at/next-to the same target, reduce
                if od_next <= 1 and myd > 1:
                    win -= 250.0

            if win > my_best_win:
                my_best_win = win

        score = risk + my_best_win