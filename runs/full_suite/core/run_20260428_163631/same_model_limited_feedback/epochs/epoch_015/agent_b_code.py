def choose_move(observation):
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        # no visible resources: move to increase separation slightly
        dx = -1 if ox > sx else (1 if ox < sx else 0)
        dy = -1 if oy > sy else (1 if oy < sy else 0)
        return [dx, dy]
    best = None
    best_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        do = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
        # Prefer resources we're closer to; secondarily prefer closer overall
        score = (ds - do, ds)
        if best_score is None or score < best_score:
            best_score = score
            best = (rx, ry)
    tx, ty = best
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh:
            continue
        if (nx, ny) in obstacles:
            continue
        nds = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        # tie-break: maximize distance from opponent to reduce interference
        ndop = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        candidates.append(((nds, -ndop), dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return [candidates[0][1], candidates[0][2]]