def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    def to_set(v):
        s = set()
        for p in v or []:
            try:
                s.add((int(p[0]), int(p[1])))
            except Exception:
                pass
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    opp_terr = to_set(observation.get("opponent_territory"))
    self_terr = to_set(observation.get("self_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(sx + dx, sy + dy, dx, dy) for dx, dy in dirs]
    neigh = [(x, y, dx, dy) for (x, y, dx, dy) in neigh if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles]

    if not neigh:
        return [0, 0]

    # Build our expansion frontier: unclaimed cells adjacent to our territory (2-step look).
    frontier = set()
    for (x, y) in self_terr:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) in unclaimed:
                frontier.add((nx, ny))
    if not frontier:
        frontier = unclaimed if unclaimed else set()

    # If opponent is present, bias towards edge conquest (entering their territory).
    opp_front = set()
    for (x, y) in self_terr:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) in opp_terr:
                opp_front.add((nx, ny))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = -10**18

    for nx, ny, dx, dy in neigh:
        # Immediate gain
        gain = 0
        if (nx, ny) in unclaimed:
            gain += 5
        if (nx, ny) in opp_terr:
            gain += 7  # flipping enabled on entry
        if (nx, ny) in self_terr:
            gain -= 1  # discourage just milling unless no options

        # Tactical bias: closer to frontier targets and slightly toward center to avoid corner trap
        tgt_bonus = 0
        if frontier:
            dmin = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in frontier)
            tgt_bonus += -0.25 * dmin
        if opp_front:
            dopp = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in opp_front) if opp_front else 0
            tgt_bonus += -0.35 * dopp

        center_bias = -0.01 * (abs(nx - cx) + abs(ny - cy))

        # Discourage being adjacent to obstacles too much
        adj_obs = 0
        for ax, ay in [(nx + dxx, ny + dyy) for dxx, dyy in dirs if (dxx, dyy) != (0, 0)]:
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                adj_obs += 1
        obstacle_pen = -0.08 * adj_obs

        score = gain + tgt_bonus + center_bias + obstacle_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]