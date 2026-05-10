def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1), (0, 0)]

    # If multiple corner targets are tied, pick deterministically based on current position.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_target():
        best = None
        bestv = None
        for cx, cy in corners:
            v = man(sx, sy, cx, cy)
            if bestv is None or v > bestv or (v == bestv and (cx < best[0] or (cx == best[0] and cy < best[1]))):
                bestv = v
                best = (cx, cy)
        return best

    tx, ty = corner_target()

    best = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_opp = man(nx, ny, ox, oy)
        # Evader prefers distance to opponent; also prefers moving toward "escape" corner.
        # Pursuer prefers decreasing distance to opponent; also avoids moving into dead-ends near corners by simplicity.
        dist_corner = man(nx, ny, tx, ty)

        # Obstacle proximity penalty to avoid getting blocked.
        prox = 0
        for ax, ay in obstacles:
            if man(nx, ny, ax, ay) == 1:
                prox += 1

        if self_is_evader:
            score = (d_opp * 1000) + (dist_corner * 3) - (prox * 50)
        else:
            score = (-d_opp * 1000) - (prox * 50) - (dist_corner * 1)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]