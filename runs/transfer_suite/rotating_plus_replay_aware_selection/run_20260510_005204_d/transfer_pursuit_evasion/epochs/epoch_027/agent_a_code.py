def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evad" in role) or ("escape" in role) or ("run" in role) or ("hide" in role) or ("runner" in role)
    if not self_is_evader and (("evad" in opp_role) or ("escape" in opp_role) or ("run" in opp_role) or ("hide" in opp_role) or ("runner" in opp_role)):
        self_is_evader = True

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    obstacles = list(blocked)

    def dist_cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def near_obst_pen(x, y):
        if not obstacles: return 0
        best = 10
        for bx, by in obstacles:
            d = dist_cheb(x, y, bx, by)
            if d < best: best = d
        return 3.0 if best <= 1 else (1.5 if best == 2 else 0.0)

    best_move = [0, 0]
    best_score = -10**18 if self_is_evader else 10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = dist_cheb(nx, ny, ox, oy)
            score = d - near_obst_pen(nx, ny) * (0.7 if self_is_evader else 1.0)
            if self_is_evader:
                if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
                    best_score, best_move = score, [dx, dy]
            else:
                score = -score  # minimize d -> maximize -d
                if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
                    best_score, best_move = score, [dx, dy]

    if best_move == [0, 0]:
        # If all moves blocked (unlikely), stay put deterministically
        return [0, 0]
    return best_move