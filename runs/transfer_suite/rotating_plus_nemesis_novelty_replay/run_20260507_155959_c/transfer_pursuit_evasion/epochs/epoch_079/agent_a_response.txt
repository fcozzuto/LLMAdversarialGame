def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.append((int(p[0]), int(p[1])))
    obs_set = set(obstacles)

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or role == "evader"

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs_set

    def nearest_obs_dist(x, y):
        if not obstacles:
            return 999
        best = 999
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    def manhattan(x, y, xx, yy):
        return abs(x - xx) + abs(y - yy)

    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_opp = manhattan(nx, ny, ox, oy)
        d_to_obs = nearest_obs_dist(nx, ny)
        if is_evader:
            key = (d_to_opp, d_to_obs, -abs(dx) - abs(dy))
        else:
            key = (-d_to_opp, d_to_obs, -abs(dx) - abs(dy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    if valid(sx, sy):
        if best_key is None:
            return [0, 0]
        return best_move
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]