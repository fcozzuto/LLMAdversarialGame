def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                obs.add((int(p[0]), int(p[1])))
            except:
                pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = set()
    for p in self_terr:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_set.add((int(p[0]), int(p[1])))
    opp_set = set()
    for p in opp_terr:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_set.add((int(p[0]), int(p[1])))
    uc_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            uc_set.add((int(p[0]), int(p[1])))

    if not uc_set and not opp_set:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Targets: prefer nearest unclaimed; if none, nearest opponent territory.
    if uc_set:
        tx, ty = min(uc_set, key=lambda t: man(sx, sy, t[0], t[1]))
    else:
        tx, ty = min(opp_set, key=lambda t: man(sx, sy, t[0], t[1]))

    # Progress direction towards opponent corner.
    prog_dx = 1 if ox > sx else (-1 if ox < sx else 0)
    prog_dy = 1 if oy > sy else (-1 if oy < sy else 0)

    best = None
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        cell_score = 0
        if (nx, ny) in opp_set:
            cell_score += 10
        elif (nx, ny) in uc_set:
            cell_score += 6
        elif (nx, ny) in self_set:
            cell_score += 2
        # Reduce distance to target
        dcur = man(sx, sy, tx, ty)
        dnew = man(nx, ny, tx, ty)
        cell_score += (dcur - dnew) * 2
        # Encourage movement towards opponent
        cell_score += (dx * prog_dx + dy * prog_dy)
        # Small bias to avoid oscillation: prefer staying closer to center line
        cx, cy = (w - 1) // 2, (h - 1) // 2
        cell_score -= (man(nx, ny, cx, cy) // 4)
        if cell_score > best_score:
            best_score = cell_score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]