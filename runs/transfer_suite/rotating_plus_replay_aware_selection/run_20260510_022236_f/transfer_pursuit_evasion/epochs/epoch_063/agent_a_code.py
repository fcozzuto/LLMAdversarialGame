def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def min_dist_to_obs(x, y):
        if not obs:
            return 999999
        best = 999999
        for px, py in obs:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        return best

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_val = None
    best_obsdist = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        man = abs(nx - ox) + abs(ny - oy)
        od = min_dist_to_obs(nx, ny)
        if is_evader:
            val = man
            # Prefer farther, and also keep away from obstacles; tie-break deterministically.
            if best is None or val > best_val or (val == best_val and od > best_obsdist) or (val == best_val and od == best_obsdist and (dx, dy) < tuple(best)):
                best, best_val, best_obsdist = [dx, dy], val, od
        else:
            val = -man  # maximizing negative distance == minimizing man
            if best is None or val > best_val or (val == best_val and od > best_obsdist) or (val == best_val and od == best_obsdist and (dx, dy) < tuple(best)):
                best, best_val, best_obsdist = [dx, dy], val, od

    if best is None:
        # If all blocked, fall back to staying put (engine will keep in place deterministically).
        return [0, 0]
    return [int(best[0]), int(best[1])]