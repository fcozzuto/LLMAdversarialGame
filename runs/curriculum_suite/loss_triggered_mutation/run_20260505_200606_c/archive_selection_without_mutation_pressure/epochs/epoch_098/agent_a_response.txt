def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose move that maximizes "win margin" on the best contested resources.
    best = None
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = 0
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds < my_best:
                my_best = ds
            if do < opp_best:
                opp_best = do
            margin = do - ds  # positive if I can reach first (faster by ds)
            # If opponent is closer, strongly incentivize reducing ds (intercept)
            if do <= ds:
                val += 2 * margin
            else:
                val += 6 * margin
            # Small penalty for being far to any high-value target
            val -= 0.08 * ds
        # If I can become the nearest overall, add bonus; otherwise reduce.
        if my_best < opp_best:
            val += 3 * (opp_best - my_best)
        else:
            val += -1.5 * (my_best - opp_best)

        if val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]