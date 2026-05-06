def choose_move(observation):
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    candidates = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    if not resources:
        # Fallback: move away from opponent, prefer staying in bounds and not into obstacles
        best = (0, -10**9, sx, sy)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            # Prefer moves that also avoid being stuck: tiny bias to center-ish
            center_bias = -abs((nx - (w - 1) / 2.0)) - abs((ny - (h - 1) / 2.0))
            val = d * 10 + center_bias
            if val > best[1]:
                best = (dx, val, nx, ny)
        return [best[0], 0] if best[0] in (-1, 0, 1) else [0, 0]

    # Choose resource where we are "ahead" versus opponent; if none, choose to maximize combined progress.
    best_target = None
    best_score = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Score: how much closer we are; tie-break by smaller our distance then by position order.
        ahead = od - sd
        score = ahead * 100 - sd
        if best_score is None or score > best_score or (score == best_score and (sd < cheb(sx, sy, best_target[0], best_target[1]))):
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target
    # Move: among valid deltas, pick one minimizing our distance to target while maximizing distance from opponent.
    best_dx, best_dy, best_val = 0, 0, -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Small deterministic tie-break favoring diagonals (probe-avoid style) and lower dx/dy ordering.
        diag_bonus = 1 if dx != 0 and dy != 0 else 0
        val = (d_opp * 2) - (d_to_t * 5) + diag_bonus
        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]