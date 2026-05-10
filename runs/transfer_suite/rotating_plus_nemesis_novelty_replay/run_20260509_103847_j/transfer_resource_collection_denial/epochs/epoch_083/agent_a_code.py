def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rset = set(tuple(p) for p in resources)
    if (sx, sy) in rset:
        return [0, 0]
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Sweep-row nemeisis: contest resources on opponent's current row; otherwise race best.
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        adv = do - ds  # >0 means we are closer
        contest = 2.0 if ry == oy else 0.0
        # Prefer intercepting sooner and not getting pinned by longer races
        key = (-(adv + contest), ds + (0.05 if ry == oy else 0.0), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Choose the best one-step move that improves contest position; if blocked, fallback.
    best_move = None
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # After moving, estimate how we compare to opponent for the chosen target.
        ns = abs(tx - nx) + abs(ty - ny)
        no = abs(tx - ox) + abs(ty - oy)
        adv2 = no - ns
        contest2 = 2.0 if ty == oy else 0.0

        # Secondary: avoid stepping onto/adjacent to obstacles (gentle smoothness).
        obs_pen = 0
        for ax, ay in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1), (nx - 1, ny - 1), (nx + 1, ny + 1), (nx - 1, ny + 1), (nx + 1, ny - 1)):
            if (ax, ay) in obstacles:
                obs_pen += 0.15

        # Tertiary: prioritize increasing closeness to target
        closer = abs(tx - sx) + abs(ty - sy) - (abs(tx - nx) + abs(ty - ny))

        key = (-(adv2 + contest2), ns + obs_pen - closer * 0.01, abs(ox - nx) + abs(oy - ny), nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]

    return best_move