def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = None
    bestc = -1
    for cx, cy in corners:
        d = abs(cx - ox) + abs(cy - oy)
        if d > bestc:
            bestc = d
            corner = (cx, cy)
    cx, cy = corner

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        # Prefer evader: maximize distance; pursuer: minimize distance
        val = (dist if is_evader else -dist) * 1000

        # Corner bias: evader toward farthest corner; pursuer toward nearest corner to opponent
        dc = abs(nx - cx) + abs(ny - cy)
        val += (-dc if is_evader else dc) * 5

        # Obstacle repulsion (soft)
        if obs:
            mind = 10**9
            for px, py in obs:
                d = abs(nx - px) + abs(ny - py)
                if d < mind:
                    mind = d
            val += (mind if is_evader else mind) * 0.5

        # Deterministic tie-breaker: lexicographic preference order by move index
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move