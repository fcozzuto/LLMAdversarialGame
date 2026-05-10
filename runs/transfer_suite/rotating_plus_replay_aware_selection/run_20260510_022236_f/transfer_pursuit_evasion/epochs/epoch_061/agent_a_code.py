def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def min_dist_to(points, x, y):
        if not points:
            return 10**9
        best = 10**9
        for px, py in points:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        return best

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue

        score = 0
        if is_evader:
            score += 5 * (abs(nx - ox) + abs(ny - oy))
        else:
            score += -5 * (abs(nx - ox) + abs(ny - oy))

        if res:
            dres = min_dist_to(res, nx, ny)
            score += -2 * dres

        # Small deterministic tie-break preference: stay longer only if equal.
        score += 0.001 * (dx * dx + dy * dy)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move