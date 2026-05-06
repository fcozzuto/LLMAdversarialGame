def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    resources = sorted([tuple(r) for r in resources], key=lambda p: (p[0] + p[1], p[0], p[1]))
    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best_move = (0, 0)
    best_score = None

    # Evaluate each possible next cell by how much it "denies" the opponent on the best available resource.
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # If blocked by obstacle, engine keeps in place; we skip invalid positions to be safe.
        margin_best = None
        self_d_best = None
        # Limit resource checks for speed/determinism
        for i in range(len(resources)):
            if i >= 10:
                break
            rx, ry = resources[i]
            if (rx, ry) in obs:
                continue
            dself = cheb(nx, ny, rx, ry)
            dopp = cheb(ox, oy, rx, ry)
            margin = dopp - dself
            if margin_best is None or margin > margin_best or (margin == margin_best and dself < self_d_best):
                margin_best = margin
                self_d_best = dself

        if margin_best is None:
            margin_best = -10**9
            self_d_best = cheb(nx, ny, w // 2, h // 2)

        # Primary: maximize denial margin. Secondary: minimize our distance to the target.
        # Tertiary: prefer staying closer to resources overall (slight).
        center_bias = -cheb(nx, ny, w // 2, h // 2) * 0.01
        score = (margin_best, -self_d_best + center_bias)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]