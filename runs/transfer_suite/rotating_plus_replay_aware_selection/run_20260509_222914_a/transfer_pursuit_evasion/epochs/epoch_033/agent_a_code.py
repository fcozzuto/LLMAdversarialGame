def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # deterministic tie-break already by move order

    obst_list = list(obstacles)

    def nearest_obst_dist(x, y):
        if not obst_list:
            return 99
        best = 10**9
        for ax, ay in obst_list:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def farthest_corner_score(x, y):
        # higher is better for evader, lower for pursuer
        best = -10**9
        for cx, cy in corners:
            d = abs(cx - x) + abs(cy - y)
            if d > best:
                best = d
        return best

    def corner_from_opponent(x, y):
        best = 10**9
        for cx, cy in corners:
            d = abs(cx - ox) + abs(cy - oy)
            # prefer staying closer to opponent's "current corner pressure" for pursuer,
            # and further from it for evader; caller handles sign via scoring.
            if d < best:
                best = d
        return best

    best_dx, best_dy = 0, 0
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        dob = nearest_obst_dist(nx, ny)

        if is_evader:
            # maximize separation, keep away from obstacles, drift toward farthest corner from opponent
            # (deterministic via pure score, no randomness)
            corner = farthest_corner_score(nx, ny)
            score = (d * 10.0) + (corner * 0.5) + (dob * 0.15)
            # small preference to not stand still unless it is best
            if dx == 0 and dy == 0:
                score -= 0.01
        else:
            # minimize separation; prefer routes that are not hugging obstacles
            corner = corner_from_opponent(nx, ny)
            score = (-d * 10.0) + (dob * 0.08) + (-corner * 0.01)
            if dx == 0 and dy == 0:
                score -= 0.005

        if best_score is None or score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]