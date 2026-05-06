def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    best = [0, 0]; best_sc = -10**18
    # Heuristic: maximize "lead" over opponent on some resource (prefer cells that increase best lead),
    # with secondary bias for shorter distance to that resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        local_best = -10**18
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            lead = od - sd  # positive means we are closer
            sc = lead * 10 - sd  # strong preference for winning contest; then faster
            # mild deny/avoid: if opponent currently closer, prefer not to move closer to that contested cell
            if od < abs(sx - rx) + abs(sy - ry):
                sc -= 2
            if sc > local_best:
                local_best = sc
        # Extra: keep stability if ties; prefer not to wander (reduce Manhattan distance to current best resource)
        if local_best > best_sc:
            best_sc = local_best; best = [dx, dy]
    return best