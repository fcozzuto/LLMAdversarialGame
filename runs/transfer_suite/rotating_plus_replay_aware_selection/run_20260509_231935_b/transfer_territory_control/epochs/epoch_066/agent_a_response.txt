def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_set = set()
    opp_set = set()
    for p in self_terr:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_set.add((int(p[0]), int(p[1])))
    for p in opp_terr:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_set.add((int(p[0]), int(p[1])))

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        is_self = (nx, ny) in self_set
        is_opp = (nx, ny) in opp_set
        # Unclaimed by either agent
        take_bonus = 0.0
        if is_opp:
            take_bonus = 3.0  # flipping opponent territory
        elif not is_self:
            take_bonus = 2.0  # claiming unclaimed cell

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        # Prefer central expansion while keeping away from opponent to avoid being outflanked
        sc = take_bonus + (-0.25 * dist_center) + (0.06 * dist_to_opp)

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]