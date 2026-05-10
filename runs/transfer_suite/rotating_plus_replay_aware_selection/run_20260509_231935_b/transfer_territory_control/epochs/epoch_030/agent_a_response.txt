def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    opp_pos = observation.get("opponent_position") or [sx, sy]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    if not unclaimed and not opp_terr:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    k = int(observation.get("turn_index", 0)) % 9
    dirs = [dirs[(i + k) % 9] for i in range(9)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    # Precompute nearest unclaimed distance (small set acceptable)
    nearest_un = None
    if unclaimed:
        bestd = 1e18
        for ux, uy in unclaimed:
            d = (ux - sx) * (ux - sx) + (uy - sy) * (uy - sy)
            if d < bestd:
                bestd = d
                nearest_un = (ux, uy)
        # Convert to sqrt only once for scoring
        nearest_un_dist = bestd ** 0.5
    else:
        nearest_un_dist = None
        nearest_un = None

    best_move = [0, 0]
    best_score = -1e18
    opp_list = list(opp_terr) if opp_terr else []
    # Use opponent territory centroid if available
    if opp_list:
        cx = sum(p[0] for p in opp_list) / len(opp_list)
        cy = sum(p[1] for p in opp_list) / len(opp_list)
    else:
        cx, cy = ox, oy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        # Territory value
        if cell in self_terr:
            base = 2.0
        elif cell in opp_terr:
            base = 5.0  # flipping opponent cell
        else:
            base = 4.0  # prefer unclaimed/unknown

        # Encourage expanding toward unclaimed, but switch to pressure if already near opponent
        # Distance components (only local, deterministic)
        d_opp = ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) ** 0.5

        if nearest_un is not None:
            d_un = ((nx - nearest_un[0]) * (nx - nearest_un[0]) + (ny - nearest_un[1]) * (ny - nearest_un[1])) ** 0.5
            # If close to opponent, prioritize pressure more
            pressure = 1.0 / (1.0 + d_opp)
            score = base + 0.8 * (nearest_un_dist - d_un) + 2.2 * pressure
        else:
            score = base + 2.2 / (1.0 + d_opp)

        # Small deterministic tie-break favoring moves that reduce Manhattan distance to opponent position
        score += -0.001 * (abs(nx - ox) + abs(ny - oy))

        if score > best_score:
            best_score = score
            best_move = [int(dx), int(dy)]

    return best_move