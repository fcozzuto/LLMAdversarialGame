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

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("evasion" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obstacle_pen(x, y):
        if not obstacles:
            return 0.0
        dmin = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < dmin:
                dmin = d
        if dmin <= 0:
            return 1e6
        if dmin == 1:
            return 200.0
        return 6.0 / (dmin + 1)

    best_score = None
    best = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist = max(abs(nx - ox), abs(ny - oy))  # capture at same cell for radius 0
        side = 1 if not is_evader else -1  # pursuer wants smaller, evader wants larger
        # Small bias toward reducing/maintaining manhattan for more "direct" motion
        manh = abs(nx - ox) + abs(ny - oy)
        pen = obstacle_pen(nx, ny)
        score = side * (1000.0 * dist + 0.5 * manh) + (pen * (1.0 if not is_evader else 0.6))

        cand = (score, dx, dy)
        if best_score is None or cand < (best_score, best[0], best[1]):
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]