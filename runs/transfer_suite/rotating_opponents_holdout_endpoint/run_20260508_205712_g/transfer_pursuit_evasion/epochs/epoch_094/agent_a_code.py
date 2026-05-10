def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in sr) or ("runner" in sr) or ("evasion" in sr)
    if ("pursuer" in sr) or ("chaser" in sr) or ("hunter" in sr):
        is_evader = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def min_obst_d2(x, y):
        if not obstacles:
            return 999999
        md = 999999
        for ax, ay in obstacles:
            d = dist2(x, y, ax, ay)
            if d < md:
                md = d
        return md

    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        od2 = dist2(nx, ny, ox, oy)
        obst_d2 = min_obst_d2(nx, ny)

        if is_evader:
            # Prefer moving away from pursuer; also prefer corners and obstacle clearance
            corner_t = max(nx, w - 1 - nx) + max(ny, h - 1 - ny)
            val = od2 * 2.0 + corner_t * 0.15 + obst_d2 * 0.02
        else:
            # Prefer moving toward pursuer; discourage getting too close to obstacles
            corner_t = max(nx, w - 1 - nx) + max(ny, h - 1 - ny)
            val = -od2 * 2.0 + corner_t * 0.02 + obst_d2 * 0.01

        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    # If all moves invalid (shouldn't happen), stay still
    return [int(best_move[0]), int(best_move[1])]