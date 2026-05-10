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

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def open_space(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    # Prefer deterministic tie-breaking by move order.
    best_move = (0, 0)
    if not is_evader:
        # Pursuer: directly reduce distance; also favor moves that keep options open and push toward a trap.
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = manh(nx, ny, ox, oy)
            # "wall pressure": prefer being closer to nearest obstacle/wall from opponent direction
            corner_bias = min(nx, ny, w - 1 - nx, h - 1 - ny)
            # open_space helps avoid running into dead-ends that evaders with obstacles exploit
            score = (-d) + 0.08 * open_space(nx, ny) - 0.02 * corner_bias
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # Evader: maximize distance; avoid corners/obstacle dead-ends while keeping mobility.
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = manh(nx, ny, ox, oy)
            corner_proximity = min(nx, ny, w - 1 - nx, h - 1 - ny)
            # Prefer staying away from tight corners and maintain mobility; also slightly bias away from opponent direction.
            score = (d) + 0.12 * open_space(nx, ny) + 0.03 * corner_proximity
            # If moving closer due to diagonal/knock, penalize
            if manh(sx, sy, ox, oy) < d:
                score += 0.05
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]