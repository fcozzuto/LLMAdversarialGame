def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def best_resource_target_value(px, py):
        if not resources:
            return None
        # Prefer nearest resource; if opponent is closer, still go but penalize letting them win.
        best_s = -10**9
        best_t = None
        for rx, ry in resources:
            d_me = cheb(px, py, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Score favors being closer, and slightly "blocking" if opponent is ahead.
            s = 200 - d_me * 10
            if d_me < d_op:
                s += 60
            else:
                s -= (d_me - d_op) * 8
            # Tie-break slightly toward central resources to reduce oscillation.
            cx = rx - (w - 1) / 2.0
            cy = ry - (h - 1) / 2.0
            s -= int(abs(cx) + abs(cy)) * 2
            if s > best_s:
                best_s, best_t = s, (rx, ry)
        return best_s, best_t

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            cand.append((dx, dy, nx, ny))

    if not cand:
        return [0, 0]

    if resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in cand:
            s, target = best_resource_target_value(nx, ny)
            if target is None:
                continue
            # Add attraction to target and repulsion from opponent to prevent easy interception.
            rx, ry = target
            v = s + (120 - cheb(nx, ny, rx, ry) * 6)
            v -= cheb(nx, ny, ox, oy) * 2
            # Mild push to avoid local cycles: prefer moves that reduce distance to target compared to current.
            v += (cheb(sx, sy, rx, ry) - cheb(nx, ny, rx, ry)) * 5
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # No visible resources: maximize distance from opponent.
    best = None
    bestv = -10**18
    for dx, dy, nx, ny in cand:
        v = cheb(nx, ny, ox, oy)
        # also avoid obstacles already handled; tie-break deterministically.
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]