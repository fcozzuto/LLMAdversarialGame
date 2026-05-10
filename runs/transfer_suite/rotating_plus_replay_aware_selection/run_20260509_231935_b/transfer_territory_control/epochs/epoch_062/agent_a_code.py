def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    try:
        sx, sy = int(sx), int(sy)
        ox, oy = int(ox), int(oy)
    except:
        return [0, 0]

    if not (0 <= sx < w and 0 <= sy < h and w > 0 and h > 0):
        return [0, 0]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    if not unclaimed:
        unclaimed = set(tuple(p) for p in (observation.get("resources") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in opp_terr:
            score += 500
        if (nx, ny) in unclaimed:
            score += 120
        if (nx, ny) in self_terr:
            score -= 80

        # Prefer moves that improve position relative to opponent
        dcur = abs(sx - ox) + abs(sy - oy)
        dnxt = abs(nx - ox) + abs(ny - oy)
        score += (dcur - dnxt) * 3

        # Small tie-breaker: move toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        score -= (abs(nx - cx) + abs(ny - cy)) * 0.01

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]