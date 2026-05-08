def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md_to_obs(x, y):
        if not obstacles:
            return 8
        best = 99
        for px, py in obstacles:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        return best

    def score(nx, ny):
        d = abs(nx - ox) + abs(ny - oy)
        if self_is_evader:
            # maximize separation; prefer safer cells
            return (d * 10.0) + (md_to_obs(nx, ny) * 0.8) - (abs(nx - (w // 2)) + abs(ny - (h // 2))) * 0.01
        else:
            # minimize separation; also avoid dead ends near obstacles
            return (-d * 10.0) + (md_to_obs(nx, ny) * 0.15) + (abs(nx - (w // 2)) + abs(ny - (h // 2))) * 0.005

    best_move = [0, 0]
    best_val = -10**18 if not self_is_evader else -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = score(nx, ny)
        # deterministic tie-breaker by move order (first seen)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move