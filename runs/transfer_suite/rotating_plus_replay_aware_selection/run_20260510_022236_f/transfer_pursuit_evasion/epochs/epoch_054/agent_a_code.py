def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role and "pursuer" not in role

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_clear(x, y):
        if not obs_set:
            return 10
        best = 0
        for ax, ay in obs_set:
            d = abs(x - ax) + abs(y - ay)
            if d < best or best == 0:
                best = d
        return best

    def center_score(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    best = None
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        clearance = obs_clear(nx, ny)
        c = center_score(nx, ny)
        if is_evader:
            val = d_opp + 0.6 * clearance + 0.05 * c
        else:
            val = -d_opp + 0.6 * clearance + 0.01 * c
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]