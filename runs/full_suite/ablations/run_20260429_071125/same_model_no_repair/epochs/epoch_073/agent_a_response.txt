def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in (observation.get("resources") or []):
        if p is not None and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Go for the corner that is farther from opponent to regain tempo.
        corners = [(0, 0), (w - 1, h - 1)]
        best_corner, best_score = corners[0], -10**18
        for cx, cy in corners:
            sdist = cheb(sx, sy, cx, cy)
            odist = cheb(ox, oy, cx, cy)
            score = (odist - sdist) - 0.1 * (sdist + odist)
            if score > best_score:
                best_score = score
                best_corner = (cx, cy)
        cx, cy = best_corner
        best_move, best_val = (0, 0), -10**18
        for dx, dy, nx, ny in legal:
            val = -cheb(nx, ny, cx, cy) - 0.05 * cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Pick a target resource where we are (deterministically) more advantaged over the opponent.
    best_r, best_rscore = resources[0], -10**18
    for rx, ry in resources:
        sdist = cheb(sx, sy, rx, ry)
        odist = cheb(ox, oy, rx, ry)
        # Prefer resources where we have a lead; break ties by earlier arrival.
        rscore = (odist - sdist) * 10 - sdist - 0.2 * odist
        if rscore > best_rscore:
            best_rscore = rscore
            best_r = (rx, ry)
    tx, ty = best_r

    # Choose the move that reduces our distance to target while also not letting opponent close the gap.
    best_move, best_val = (0, 0), -10**18
    for dx, dy, nx, ny in legal:
        sdist_now = cheb(sx, sy, tx, ty)
        sdist_next = cheb(nx, ny, tx, ty)

        odist_to_t = cheb(ox, oy, tx, ty)
        # Opponent cannot be influenced directly; approximate by preferring states that keep
        # our lead over the opponent (higher is better).
        lead_next = odist_to_t - sdist_next

        # Small secondary: avoid moving closer to opponent (break ties).
        val = (lead_next * 10) + (sdist_now - sdist_next) - 0.03 * cheb(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]