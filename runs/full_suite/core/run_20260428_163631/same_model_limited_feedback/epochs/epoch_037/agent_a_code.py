def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = set(tuple(p) for p in (observation["obstacles"] or []))
    res = [tuple(p) for p in resources if 0 <= p[0] < w and 0 <= p[1] < h]
    dirs = (-1, 0, 1)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx if dx >= 0 else -dx if dx != 0 else 0

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose target resource based on who can arrive sooner (our advantage), otherwise fight over nearest.
    if res:
        best = None
        best_val = -10**9
        for rx, ry in res:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer securing resources we can reach earlier; if tie, prefer farther from opponent (reduce contest).
            val = (do - ds) * 10 - ds + (dist(rx, ry, sx, sy) <= dist(rx, ry, ox, oy)) * 0
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources: try to move to center-ish to avoid getting stuck.
        tx, ty = w // 2, h // 2

    # Evaluate each move; also incorporate opponent blocking when we can't secure targets.
    options = []
    for dx in dirs:
        for dy in dirs:
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            self_to = dist(nx, ny, tx, ty)
            opp_to = dist(ox, oy, tx, ty)
            # If opponent already closer to target, prioritize increasing their distance and reducing their ability to take other resources.
            opp_move = dist(nx, ny, ox, oy)
            # Encourage moving toward target while keeping some separation.
            score = -self_to * 5 + (dist(ox, oy, tx, ty) - self_to) * 3 + opp_move * 0.1
            # Add mild obstacle avoidance by penalizing moves adjacent to many obstacles.
            adj = 0
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    if ex == 0 and ey == 0:
                        continue
                    ax, ay = nx + ex, ny + ey
                    if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                        adj += 1
            score -= adj * 0.2
            options.append((score, dx, dy))

    if not options:
        return [0, 0]
    options.sort(key=lambda t: (t[0], -t[1], -t[2]))
    return [int(options[-1][1]), int(options[-1][2])]