def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = (observation.get("self_role", "") or "").lower()

    is_pursuer = ("purs" in self_role) or ("hunt" in self_role) or ("seek" in self_role) or ("chase" in self_role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx if dx > dy else dy

    # Predict opponent (assume evader increases distance; pursuer minimizes distance). One-step kinematics only.
    if ox == sx:
        stepx = 0
    else:
        stepx = 1 if ox > sx else -1
    if oy == sy:
        stepy = 0
    else:
        stepy = 1 if oy > sy else -1

    if is_pursuer:
        px = clamp(ox + stepx, 0, w - 1)
        py = clamp(oy + stepy, 0, h - 1)
        # Choose a move that reduces distance to predicted opponent position.
        best = None
        best_score = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_pred = cheb(nx, ny, px, py)
            d_now = cheb(nx, ny, ox, oy)
            # Tie-breaker: also move toward furthest corner to avoid being kited into one side.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            furthest = max(corners, key=lambda c: cheb(nx, ny, c[0], c[1]))
            dist_corner = cheb(nx, ny, furthest[0], furthest[1])
            score = d_pred * 1000 + d_now * 10 + (dist_corner % 7)
            if score < best_score:
                best_score = score
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    else:
        # Evader: move to maximize distance from pursuer, while avoiding obstacles and preferring corners.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
        best = None
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, target_corner[0], target_corner[1])
            # Small deterministic preference: prefer staying away from center if corner-targeted.
            d_center = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
            score = d * 1000 + d_corner * 10 + d_center
            if score > best_score:
                best_score = score
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]