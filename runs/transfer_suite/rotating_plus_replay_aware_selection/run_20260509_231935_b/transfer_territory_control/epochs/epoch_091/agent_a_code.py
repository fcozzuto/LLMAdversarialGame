def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    inside = lambda x, y: 0 <= x < w and 0 <= y < h
    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = set((int(p[0]), int(p[1])) for p in self_terr if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) == 2)
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) == 2)

    # Ensure we have some target even if unclaimed_cells is empty
    if not un_set:
        # Fallback: treat cells adjacent to our territory as "unclaimed-like" targets
        for (x, y) in list(self_set)[:]:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and (nx, ny) not in obs and (nx, ny) not in self_set and (nx, ny) not in opp_set:
                    un_set.add((nx, ny))

    # Also consider capturing neighbor boundary around opponent
    opp_boundary = set()
    for (x, y) in opp_set:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                opp_boundary.add((nx, ny))
    if not opp_boundary:
        opp_boundary = set(opp_set)

    def min_dist(pos_set, x, y, limit=64):
        if not pos_set:
            return limit
        best = limit
        for (tx, ty) in pos_set:
            d = abs(x - tx) + abs(y - ty)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    best_move = (0, 0)
    best_score = None

    # Deterministic tie-breaker: fixed order dirs
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        # Scoring
        if (nx, ny) in opp_set:
            score = 1000 - (abs(nx - sx) + abs(ny - sy))
        elif (nx, ny) in un_set:
            score = 200 - (abs(nx - sx) + abs(ny - sy))
        elif (nx, ny) in self_set:
            score = 50 - (abs(nx - sx) + abs(ny - sy))
        else:
            score = 10

        # Push towards contested/unclaimed areas, but prioritize opponent boundary
        d_opp = min_dist(opp_boundary, nx, ny, limit=32)
        d_un = min_dist(un_set, nx, ny, limit=32)

        # If moving into opponent boundary neighborhood, increase urgency (counterclaim behavior)
        score += (60 - 2 * d_opp)
        score += (20 - 2 * d_un)

        # Mild preference for staying away from obstacles is already handled by legality; add center bias
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= 0.01 * (abs(nx - cx) + abs(ny - cy))

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]