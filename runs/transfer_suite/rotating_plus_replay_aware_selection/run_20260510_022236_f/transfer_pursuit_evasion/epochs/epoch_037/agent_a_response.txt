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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        if nx == ox and ny == oy:
            if not is_evader:
                return [dx, dy]
        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy
        wd = wall_dist(nx, ny)

        # Tie-break deterministically by move order (first seen on equal score).
        if is_evader:
            # Maximize distance; prefer staying away from walls (center-seeking).
            score = (d2 * 4) + (wd * 0.6)
        else:
            # Minimize distance; also prefer moves that keep some clearance from walls.
            score = (-d2 * 4) + (wd * 0.2)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]