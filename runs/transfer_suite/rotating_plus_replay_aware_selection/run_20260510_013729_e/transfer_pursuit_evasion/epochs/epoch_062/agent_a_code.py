def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("hunter" in self_role) or ("pursue" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    obs_list = list(obs)

    def min_dist_to_obstacle(x, y):
        if not obs_list:
            return 99
        md = 99
        for ax, ay in obs_list:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_val = None
    best_delta = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if is_pursuer:
            dist_term = -d
            mobility = min_dist_to_obstacle(nx, ny)
            # Prefer being close to target while not moving into tight obstacle neighborhoods.
            val = dist_term + 0.05 * mobility
        else:
            dist_term = d
            mobility = min_dist_to_obstacle(nx, ny)
            # Keep away from pursuer and obstacles.
            val = dist_term + 0.25 * mobility
        if best_val is None or val > best_val or (val == best_val and [dx, dy] < best_delta):
            best_val = val
            best_delta = [dx, dy]

    # If all candidate moves blocked, stay still (deterministic).
    return best_delta if best_val is not None else [0, 0]