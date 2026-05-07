def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Evaluate a move by the best "race advantage" it creates on remaining resources.
    best_val = -10**18
    best_tie = 10**18
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        self_min = 10**9
        opp_min = 10**9
        best_gap = -10**18
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gap = do - ds  # positive means we arrive no later than opp on that resource
            if gap > best_gap:
                best_gap = gap
            if ds < self_min:
                self_min = ds
            if do < opp_min:
                opp_min = do

        # Prefer larger gap; then shorter self_min; then larger opp_min (reduce their chance).
        val = best_gap * 1000 - self_min
        tie = (self_min, -opp_min)
        if val > best_val or (val == best_val and (tie < best_tie)):
            best_val = val
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]