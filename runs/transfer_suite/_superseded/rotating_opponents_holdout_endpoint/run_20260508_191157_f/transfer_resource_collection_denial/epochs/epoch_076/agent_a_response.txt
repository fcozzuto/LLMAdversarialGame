def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        # Go to the farthest corner opposite to opponent to reduce denial
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
        best = [0, 0]
        bestv = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = manh(nx, ny, tx, ty)
            if d < bestv or (d == bestv and (dx*dx + dy*dy) < (best[0]*best[0] + best[1]*best[1])):
                bestv = d
                best = [dx, dy]
        return best

    # Choose a target resource: prefer ones we can reach earlier; otherwise best contested.
    best_score = -10**18
    best_t = None
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # If we're earlier, strong preference; if later, discourage heavily.
        score = (opd - myd) * 1000 - myd
        # If very close, prioritize directly collecting.
        if myd <= 1:
            score += 50000
        if opd <= 1 and myd > 1:
            score -= 60000
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t

    # One-step greedy that also avoids stepping into bad competition zone.
    # Primary: reduce distance to target. Secondary: maximize advantage over opponent.
    best = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = manh(nx, ny, tx, ty)
        myd_next = nd
        opd_next = manh(ox, oy, tx, ty)
        advantage = opd_next - myd_next
        # Prefer smaller nd; larger advantage. Deterministic tie-break by move preference order.
        move_cost = dx*dx + dy*dy
        key = (nd, -advantage, move_cost, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    # Fallback (shouldn't happen if at least one move valid)
    if best == [0, 0] and not valid(sx, sy):
        return [0, 0]
    return best