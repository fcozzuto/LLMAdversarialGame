def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy)) if not is_evader else max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_corner = abs(nx - tx) + abs(ny - ty)
        d_wall = min(nx, ny, (w - 1) - nx, (h - 1) - ny)

        # Prefer staying away from obstacles; stronger for adjacent.
        min_d_obs = 10**9
        for ax, ay in obs:
            dd = abs(nx - ax) + abs(ny - ay)
            if dd < min_d_obs:
                min_d_obs = dd
        if min_d_obs == 0:
            continue
        obs_score = 0
        if min_d_obs == 1:
            obs_score = -120
        elif min_d_obs == 2:
            obs_score = -25
        elif min_d_obs <= 4:
            obs_score = -6
        else:
            obs_score = 2

        if is_evader:
            # Maximize survival: increase distance to pursuer; also drift toward safe corner.
            score = (d_opp * 10) + (d_corner * -0.2) + (d_wall * 1.5) + obs_score
        else:
            # Pursuer: decrease distance to evader; avoid walls/obstacles slightly; bias toward evader's corner.
            score = (d_opp * -12) + (d_corner * -0.3) + (d_wall * 0.2) + obs_score

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move