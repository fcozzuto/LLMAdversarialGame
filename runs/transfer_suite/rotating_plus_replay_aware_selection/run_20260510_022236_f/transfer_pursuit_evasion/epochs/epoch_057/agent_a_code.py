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

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def near_obs_penalty(x, y):
        if not obs_set:
            return 0
        best = 999
        for ax, ay in obs_set:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
                if best == 0:
                    return 50
                if best == 1:
                    return 20
                if best == 2:
                    return 8
        return 0 if best > 2 else (12 if best == 3 else 0)

    best_move = [0, 0]
    if not is_evader:
        best_score = 10**9
        # Pursuer: minimize distance, avoid obstacles, prefer moves that reduce dx/dy separately.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obs_set:
                continue
            d = manh(nx, ny, ox, oy)
            # small tie-break: move closer on the dominant axis
            if abs(ox - nx) + abs(oy - ny) == d:
                pass
            axis = (0 if abs(ox - nx) < abs(ox - sx) else 1) + (0 if abs(oy - ny) < abs(oy - sy) else 1)
            score = d + near_obs_penalty(nx, ny) * 0.7 + axis * 0.01
            if score < best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # Evader: maximize distance, avoid obstacles, and bias away from opponent.
    best_score = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        d = manh(nx, ny, ox, oy)
        # Prefer moving toward farthest corner only when it doesn't fight obstacle avoidance.
        corner_dist = max(ny + nx, ny + (w - 1 - nx), (h - 1 - ny) + nx, (h - 1 - ny) + (w - 1 - nx))
        score = d * 1.0 + corner_dist * 0.02 - near_obs_penalty(nx, ny) * 0.9
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move