def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort()

    tx = 0 if ox == sx else (1 if ox > sx else -1)
    ty = 0 if oy == sy else (1 if oy > sy else -1)

    def obst_pen(x, y):
        if not obstacles: return 0
        best = 10**9
        for a, b in obstacles:
            d = abs(x - a) + abs(y - b)
            if d < best: best = d
        if best == 10**9: return 0
        return 2.0 / (best + 1)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        man = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        align = (dx == tx) + (dy == ty) + (dx == 0 and tx == 0) + (dy == 0 and ty == 0)
        # Pursuer: minimize capture distance, strongly follow target direction.
        # Evader: maximize distance and prefer moves that keep direction away from pursuer.
        if is_evader:
            # favor stepping away in both axes; avoid obstacles moderately
            away = (dx == -tx) + (dy == -ty)
            score = (-man * 3.0) + (-cheb * 1.0) + (-away * 2.0) - obst_pen(nx, ny)
        else:
            score = (man * 3.0) + (cheb * 1.0) - (align * 2.0) + obst_pen(nx, ny)
        if best_score is None or (is_evader and score < best_score) or (not is_evader and score < best_score):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]