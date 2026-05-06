def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

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

    def blocked(x, y):
        return (x, y) in obstacles

    if not resources:
        return [0, 0]

    # Choose a target I can reach relatively earlier than the opponent.
    best_t = None
    best_val = -10**9
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        val = (opd - myd) * 3 - myd  # strong preference for resources I'm closer to
        # If I'm not closer, still prefer not-too-far.
        if opd - myd < 0:
            val -= (myd - opd) * 2
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t

    # Evaluate neighbor moves: minimize distance to target, avoid getting too close to opponent, avoid obstacles/out of bounds.
    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            d_to_t = cheb(nx, ny, tx, ty)
            d_to_o = cheb(nx, ny, ox, oy)
            # Score: prefer smaller target distance; prefer keeping some distance from opponent.
            score = -d_to_t * 10 + d_to_o
            # Additional bias: don't step adjacent to opponent unless also very close to target.
            if d_to_o <= 1:
                score -= 6 * (d_to_t + 1)
            # Small deterministic tie-breaker towards staying within bounds "diagonally" (prefer dx,dy close to 0)
            score -= (abs(dx) + abs(dy)) * 0.01
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]