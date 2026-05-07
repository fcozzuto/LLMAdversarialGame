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

    # Pre-parse resources
    res = [(int(x), int(y)) for x, y in resources]
    best = None  # (score, dx, dy)

    for dx, dy, nx, ny in legal:
        self_min = 10**9
        opp_min = 10**9
        self_sum = 0
        opp_sum = 0
        nearest_res = None
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            self_sum += ds
            opp_sum += do
            if ds < self_min:
                self_min = ds
                nearest_res = (rx, ry)
            if do < opp_min:
                opp_min = do
        # Choose moves that (1) make us reach a resource sooner than opponent,
        # (2) reduce our distance strongly, (3) increase opponent's pressure.
        # Add small tie-break toward smaller total distance and toward advancing to nearest_res.
        self_to_nearest = cheb(nx, ny, nearest_res[0], nearest_res[1]) if nearest_res else 0
        adv = opp_min - self_min
        score = 1000 * adv - 10 * self_min + 2 * (opp_sum - self_sum) - self_to_nearest
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]