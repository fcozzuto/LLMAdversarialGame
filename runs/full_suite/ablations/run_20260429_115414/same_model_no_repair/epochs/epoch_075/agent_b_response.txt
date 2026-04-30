def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def passable(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs.sort(key=lambda d: (d[0], d[1]))  # deterministic

    def cell_score(nx, ny):
        if not passable(nx, ny):
            return -10**9
        if not resources:
            # Head toward center while keeping away from obstacles
            best_obst = min((dist_cheb(nx, ny, ex, ey) for ex, ey in obstacles), default=10)
            return (best_obst * 3) - dist_cheb(nx, ny, w // 2, h // 2)

        # Choose the resource we can get with best advantage
        best_adv = -10**18
        best_res = None
        for rx, ry in resources:
            ds = dist_cheb(nx, ny, rx, ry)
            do = dist_cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            if adv > best_adv or (adv == best_adv and ((rx, ry) < best_res if best_res is not None else True)):
                best_adv = adv
                best_res = (rx, ry)

        # Obstacle avoidance: penalize closeness to obstacles near the move
        min_obst = min((dist_cheb(nx, ny, ex, ey) for ex, ey in obstacles), default=10)
        obst_pen = 0
        if min_obst <= 1:
            obst_pen = 8
        elif min_obst == 2:
            obst_pen = 3

        # Small tie-break: prefer being closer to opponent (can contest), but only mildly
        contest = dist_cheb(nx, ny, ox, oy)
        return (best_adv * 10) + (min_obst) - obst_pen - contest

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = cell_score(nx, ny)
        if v > best_val or (v == best_val and [dx, dy] < best_move):
            best_val = v
            best_move = [dx, dy]
    if not passable(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return best_move