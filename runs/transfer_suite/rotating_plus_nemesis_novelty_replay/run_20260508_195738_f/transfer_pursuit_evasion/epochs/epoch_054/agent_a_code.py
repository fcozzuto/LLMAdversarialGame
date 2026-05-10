def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def nearest_obs_d2(x, y):
        best = 10**9
        for ox2, oy2 in obs:
            d2 = dist2(x, y, ox2, oy2)
            if d2 < best:
                best = d2
        return best if obs else best

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d2 = dist2(nx, ny, ox, oy)
        obs_d2 = nearest_obs_d2(nx, ny)
        # Prefer staying away from obstacles; also bias to corners to reduce capture paths.
        corner_bias = (nx in (0, w - 1) or ny in (0, h - 1))
        # If evader: maximize distance; if pursuer: minimize distance.
        val = d2 if is_evader else -d2
        val += 0.35 * obs_d2**0.5  # away from obstacles
        val += (0.25 if corner_bias else 0.0)

        if best_val is None or (val > best_val if is_evader else val > best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]