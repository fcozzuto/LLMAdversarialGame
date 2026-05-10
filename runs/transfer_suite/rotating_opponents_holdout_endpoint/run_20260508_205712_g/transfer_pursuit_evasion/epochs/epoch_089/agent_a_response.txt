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
    is_evader = ("evader" in sr) or ("runner" in sr)
    if ("pursuer" in sr) or ("chaser" in sr) or ("hunter" in sr):
        is_evader = False

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_score = None
    # tie-break order is deterministic by move list order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance
        score = -d if not is_evader else d
        # extra nudge: prefer moving "toward" center for evader, "toward" opponent for pursuer in tie
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_term = (-(abs(nx - cx) + abs(ny - cy)) if is_evader else (abs(nx - cx) + abs(ny - cy)))
        score = (score * 1000) + int(center_term)
        if best is None or score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]