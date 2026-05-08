def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def parse_pos_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p is None or len(p) < 2:
                continue
            s.add((int(p[0]), int(p[1])))
        return s

    obstacles = parse_pos_set("obstacles")
    selfT = parse_pos_set("self_territory")
    oppT = parse_pos_set("opponent_territory")
    unclaimed = parse_pos_set("unclaimed_cells")
    resources = parse_pos_set("resources")

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist1(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    # Choose targets: resources > unclaimed > general frontier (unclaimed near us)
    target_set = resources if resources else unclaimed
    if not target_set and unclaimed:
        target_set = unclaimed

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if dx == 0 and dy == 0:
            pass
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base value for immediate control swing
        gain = 0
        if (nx, ny) in selfT:
            gain += 1
        if (nx, ny) in unclaimed:
            gain += 2
        if (nx, ny) in oppT:
            gain += 6  # likely flips territory control on entry

        # Frontier pressure: prefer moving closer to unclaimed/resources if available
        pressure = 0
        if target_set:
            pressure -= min(dist1((nx, ny), t) for t in target_set)

        # Counterclaim pressure: prefer being close to opponent territory
        if oppT:
            pressure -= 0.6 * min(dist1((nx, ny), t) for t in oppT)

        # Keep away from obstacles slightly
        obstacle_adj = 0
        for adx, ady in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            ax, ay = nx + adx, ny + ady
            if inside(ax, ay) and (ax, ay) in obstacles:
                obstacle_adj += 1
        risk = -0.3 * obstacle_adj

        # Tie-break: deterministic preference for moves that reduce distance to center and opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_tie = -0.01 * (abs(nx - cx) + abs(ny - cy))
        opp_tie = -0.02 * dist1((nx, ny), (ox, oy))

        score = (gain, pressure, risk, center_tie, opp_tie, -abs(dx) - abs(dy))
        candidates.append((score, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]