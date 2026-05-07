def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_key = None
    best_move = (0, 0)

    # Greedy one-step lookahead: choose move that maximizes expected "lead" to the best reachable resource,
    # while mildly preferring obstacle-safe advancement and blocking (favor moves that reduce opponent access).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Find best resource for us after this move
        best_for_move = None
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            lead = opd - myd  # positive means we are closer than opponent
            # Tie-break to reduce brittleness: prefer nearer resources and positions closer to bottom-right quadrant
            key = (lead, -myd, (rx - (w - 1) / 2) ** 2 + (ry - (h - 1) / 2) ** 2)
            if best_for_move is None or key > best_for_move[0]:
                best_for_move = (key, (rx, ry), myd, opd)

        if best_for_move is None:
            continue

        key, (rx, ry), myd, opd = best_for_move
        # Blocking term: if opponent is closer to some resource, reduce their approach by moving to increase their distance to that resource.
        opp_dist_here = man(ox, oy, rx, ry)
        my_advance = man(sx, sy, rx, ry) - myd
        block = 0.5 * (opp_dist_here - man(ox, oy, nx, ny))  # heuristic
        safe = 0
        for adx, ady in dirs:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                safe += 1

        final_key = (key[0] + 0.1 * my_advance + block, -myd, safe, dx, dy)
        if best_key is None or final_key > best_key:
            best_key = final_key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]