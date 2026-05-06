def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0:
            d1 = -d1
        d2 = y1 - y2
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    legal_self = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal_self.append((dx, dy, nx, ny))
    if not legal_self:
        return [0, 0]

    legal_opp = []
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal_opp.append((nx, ny))
    if not legal_opp:
        legal_opp = [(ox, oy)]

    if not resources:
        # Hold position unless it helps avoid immediate opposition pursuit
        best = (-10**9, 0, 0, 0)
        for dx, dy, nx, ny in legal_self:
            dist_opp = md(nx, ny, ox, oy)
            key = (dist_opp, -abs(nx - (w - 1)) - abs(ny - (h - 1)), dx, dy)
            if key > best:
                best = key
        return [best[2], best[3]]

    # Choose move that maximizes "guaranteed" advantage vs opponent after their one-step response.
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal_self:
        # Prefer resources we can get closer to, and also those where opponent cannot overtake after 1 step.
        local = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = min(md(px, py, rx, ry) for (px, py) in legal_opp)  # opponent's best next distance
            # Larger od - sd is better (we are closer after response). Tie-break on shorter self distance.
            key = (od - sd, -sd, -abs(nx - rx) - abs(ny - ry), rx, ry)
            if local is None or key > local:
                local = key
        if local is None:
            continue
        # Extra deterministic tiebreak: prefer staying closer to center-ish to avoid edge trapping
        center_bias = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        final_key = (local[0], local[1], local[2], center_bias, -dx * dx - dy * dy, dx, dy)
        if best_key is None or final_key > best_key:
            best_key = final_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]