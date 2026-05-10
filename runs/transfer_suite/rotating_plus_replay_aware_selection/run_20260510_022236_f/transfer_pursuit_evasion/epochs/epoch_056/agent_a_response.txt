def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

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

    def obs_near_penalty(x, y):
        # High when moving adjacent to obstacles; lower far away
        if not obs_set:
            return 0
        best = 999
        for ax, ay in obs_set:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
                if best == 0:
                    return 10
        if best == 0:
            return 10
        if best == 1:
            return 5
        if best == 2:
            return 2
        return 0

    def score_for(x, y):
        # Pursuer: minimize dist to opponent. Evader: maximize.
        d_to = abs(x - ox) + abs(y - oy)
        edge = min(x, y, w - 1 - x, h - 1 - y)
        edge_bias = (7 - edge)  # prefer central squares a bit
        obs_pen = obs_near_penalty(x, y)

        if is_evader:
            return (-d_to * 3) - edge_bias - obs_pen * 2
        else:
            return (d_to * 3) + edge_bias + obs_pen * 2

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        val = score_for(nx, ny)
        if best_val is None or val < best_val or (val == best_val and (nx, ny) < best):
            best_val = val
            best = (nx, ny)

    if best is None:
        return [0, 0]
    bx, by = best
    return [bx - sx, by - sy]