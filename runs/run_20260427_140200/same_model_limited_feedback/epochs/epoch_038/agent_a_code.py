def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # Moves in deterministic priority: straight/diagonal toward target, then alternatives
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Fallback: drift toward center but avoid obstacles if possible
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if (nx < 0 or nx >= w or ny < 0 or ny >= h) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]
    # Choose target resource: prefer closest; tie-break by coordinates
    best_r = None
    best_d = 10**9
    for rx, ry in resources:
        d = abs(rx - sx) + abs(ry - sy)
        if d < best_d or (d == best_d and (rx, ry) < best_r):
            best_d = d
            best_r = (rx, ry)
    tx, ty = best_r
    # Secondary: mild competition pressure toward resources closer to opponent
    opp_prefer = []
    for rx, ry in resources:
        opp_prefer.append((abs(rx - ox) + abs(ry - oy), rx, ry))
    opp_prefer.sort()
    # Evaluate candidate moves by resulting position
    best = (10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if (nx < 0 or nx >= w or ny < 0 or ny >= h) or (nx, ny) in obstacles:
            continue
        dist_me = abs(tx - nx) + abs(ty - ny)
        # If move captures/lands on a resource, prioritize heavily
        capture_bonus = -1000 if (nx, ny) in resources else 0
        # Prevent giving opponent an easy grab: penalize positions that bring opponent much closer
        dist_opp = abs(tx - ox) + abs(ty - oy)
        # Compare new distance from opponent to chosen target only (static target)
        new_opp_dist = abs(tx - ox) + abs(ty - oy)
        # Also mildly prefer decreasing distance to opponent (to contest) if it doesn't harm resource pursuit
        contest = (abs(ox - nx) + abs(oy - ny))
        # Scoring
        score = dist_me + contest * 0.05 + new_opp_dist * 0.0 + capture_bonus
        if score < best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)
    return [best[1], best[2]]