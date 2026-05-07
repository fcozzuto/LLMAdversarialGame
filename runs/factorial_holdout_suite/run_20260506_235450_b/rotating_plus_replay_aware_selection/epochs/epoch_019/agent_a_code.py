def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Prefer resources we can reach earlier than opponent; if close, keep a "safe" lead.
    best = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive means we are faster
        # Slightly prefer resources further away from opponent to avoid late steals.
        opp_far = cheb(ox, oy, rx, ry)
        # Deterministic lexicographic: (lead, -opp_far, -sd)
        cand = (lead, -opp_far, -sd, rx, ry)
        if best is None or cand > best:
            best = cand

    _, _, _, tx, ty = best

    # Choose the move that best reduces our distance to the chosen target, without moving into obstacles.
    best_move = None
    best_key = None
    for dx, dy, nx, ny in legal:
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Also ensure we don't hand the opponent a perfect next-step steal opportunity.
        # If we move onto our target, that's top priority via nsd=0.
        steal_risk = 0
        if cheb(ox, oy, tx, ty) <= 1 and nsd > 0:
            steal_risk = 1
        key = (-nsd, steal_risk, -nod, nx, ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]