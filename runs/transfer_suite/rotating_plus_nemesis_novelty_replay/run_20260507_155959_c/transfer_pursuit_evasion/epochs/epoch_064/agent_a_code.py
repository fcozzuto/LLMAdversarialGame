def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    obs_list = list(obstacles)

    def nearest_obstacle_clearance(x, y):
        if not obs_list:
            return 99
        md = 99
        for ax, ay in obs_list:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role)

    best_move = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        clear = nearest_obstacle_clearance(nx, ny)

        if is_evader:
            # maximize distance; prefer moving away from obstacles
            key = (-dist, -clear, dx, dy)
        else:
            # minimize distance; prefer moving away from obstacles
            key = (dist, -clear, dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move