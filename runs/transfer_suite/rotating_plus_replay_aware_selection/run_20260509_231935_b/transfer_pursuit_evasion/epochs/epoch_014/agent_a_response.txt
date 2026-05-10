def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs_set.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in sr) and ("evad" not in orr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def mobility(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs_set:
                cnt += 1
        return cnt

    def walliness(x, y):
        adj = 0
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs_set:
                adj += 1
        return adj

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)
        if not self_is_evader:
            # Pursuer: minimize distance, prefer mobility to avoid getting stuck.
            score = (-d, mob, -abs(nx - sx) - abs(ny - sy))
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)
        else:
            # Evader: maximize distance, hug walls, avoid low-mobility traps.
            corners = (nx in (0, w - 1) and ny in (0, h - 1))
            score = (d, walliness(nx, ny), corners, mob)
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]