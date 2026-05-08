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

    moves = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_evader = ("evader" in sr) or ("runner" in sr)
    opp_evader = ("evader" in orr) or ("runner" in orr)
    # If opponent_role is missing, infer from environment/pursuit_evasion: evader likely tries to increase distance.
    if ("evader" not in orr) and ("pursuer" in orr or "chaser" in orr or "cop" in orr):
        opp_evader = False
    if ("pursuer" not in orr) and ("evader" not in orr) and ("runner" not in orr) and ("chaser" not in orr):
        if self_evader:
            opp_evader = False
        else:
            opp_evader = True

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_opp_move(ax, ay, tx, ty):
        best = None
        for dx, dy in moves:
            nx, ny = tx + dx, ty + dy
            if not free(nx, ny):
                continue
            d = dist(ax, ay, nx, ny)
            score = d if opp_evader else -d
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Evaluate self one-step with opponent one-step response.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not free(nsx, nsy):
            continue
        odx, ody = best_opp_move(nsx, nsy, ox, oy)
        nosx, nosy, noox, nooy = nsx, nsy, ox + odx, oy + ody
        d = dist(nosx, nosy, noox, nooy)
        # pursuer wants small distance; evader wants large distance
        score = d if self_evader else -d
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move