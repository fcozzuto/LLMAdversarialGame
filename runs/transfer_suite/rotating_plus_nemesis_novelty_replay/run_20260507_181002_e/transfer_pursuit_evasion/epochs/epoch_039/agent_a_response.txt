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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    sr = str(observation.get("self_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    # If roles are explicit, trust it when possible
    if not self_is_evader:
        orr = str(observation.get("opponent_role", "")).lower()
        if ("evader" in orr) or ("runner" in orr):
            self_is_evader = False

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = [0, 0]
    if self_is_evader:
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            score = d * 1000 - (abs(dx) + abs(dy))  # prefer closer distance first, deterministic tie-break
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        best_score = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            score = d * 1000 + (abs(dx) + abs(dy))  # deterministic tie-break
            if score < best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]