def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    opp_cells = list(opp_t)
    unclaimed_list = list(unclaimed)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cxands = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cxands.append((nx, ny, dx, dy))

    def min_manhattan(px, py, cells):
        md = 10**9
        for x, y in cells:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md if cells else md

    # Heuristic weights: grab unclaimed, threaten/enter opponent territory, stay away from obstacles already present.
    opp_min_from_candidates = []
    for nx, ny, dx, dy in cxands:
        if opp_cells:
            d_opp = min_manhattan(nx, ny, opp_cells)
        else:
            d_opp = 10**6
        opp_min_from_candidates.append((nx, ny, dx, dy, d_opp))

    # Prefer unclaimed cells that are close to opponent territory (counterclaim).
    best_target = None
    if unclaimed_list and opp_cells:
        for x, y in unclaimed_list:
            if (x, y) in blocked:
                continue
            d = min_manhattan(x, y, opp_cells)
            if best_target is None or d < best_target[0] or (d == best_target[0] and abs(x - sx) + abs(y - sy) < best_target[1]):
                best_target = (d, abs(x - sx) + abs(y - sy), x, y)
    tx, ty = (best_target[2], best_target[3]) if best_target else (sx, sy)

    # Also bias toward moving along diagonal/frontier to reduce distance to target.
    best_move = [0, 0]
    best_score = -10**18
    for nx, ny, dx, dy, d_opp in opp_min_from_candidates:
        score = 0
        if (nx, ny) in unclaimed:
            score += 10
        if (nx, ny) in opp_t:
            score += 7  # flipping on entry is enabled
        if (nx, ny) in self_t:
            score += 1  # consolidate
        score += max(0, 6 - d_opp) * 0.8  # approach opponent territory to force flips
        score += -0.15 * (abs(nx - tx) + abs(ny - ty))
        # Avoid getting stuck: slight penalty if we'd remain in place while far from target
        if dx == 0 and dy == 0 and (abs(sx - tx) + abs(sy - ty) > 2):
            score -= 2.5
        # Small tie-breaker toward decreasing distance to opponent to counteract passive paths
        score += -0.02 * (abs(nx - (observation.get("opponent_position", (sx, sy))[0])) + abs(ny - (observation.get("opponent_position", (sx, sy))[1])))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]