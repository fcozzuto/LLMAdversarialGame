def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def legal(nx, ny): return inb(nx, ny) and (nx, ny) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    if resources:
        # Keep resource list ordered deterministically (by distance then coordinates)
        res_sorted = sorted(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
        res_sorted = res_sorted[:6]
    else:
        res_sorted = []

    # Obstacle proximity penalty (deterministic nearest-distance)
    def obs_pen(x, y):
        if not obstacles:
            return 0
        best = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
                if best == 0:
                    break
        if best == 0:
            return 10**6
        if best == 1:
            return 30
        if best == 2:
            return 10
        return 0

    # Strategic mode switch to avoid repeating same behavior
    race_mode = (int(observation.get("turn_index", 0)) % 2 == 0)

    best = None
    best_score = -10**18
    tx, ty = w // 2, h // 2

    for dx, dy, nx, ny in legal_moves:
        score = -0.2 * cheb(nx, ny, tx, ty)  # central pressure
        score -= obs_pen(nx, ny)

        if res_sorted:
            # Evaluate move by how much it improves our lead over opponent on nearby resources
            local = 0
            for rx, ry in res_sorted:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                lead = opd - myd
                # Encourage decisive leads; slightly discourage long travel
                local += (3.0 * lead - 0.15 * myd)
                if race_mode:
                    # Race: heavily reward any resource where we are closer than opponent
                    if myd <= opd:
                        local += 4.0
                else:
                    # Intercept/deny: prefer moves that reduce opponent advantage
                    if opd < myd:
                        local -= 2.0
            score += local
        else:
            # No visible resources: move to reduce distance to opponent (potential denial)
            score += 0.15 * (cheb(ox, oy, nx, ny) * -1)

        # Deterministic tie-break by move order
        if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1]) if best else True):
            best_score = score
            best = (dx, dy, nx, ny)

    return [best[0], best[1]]