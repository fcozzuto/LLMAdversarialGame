def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    # Target: nearest unclaimed; if none, move toward opponent to enable flipping on contact.
    if unclaimed:
        target = min(unclaimed, key=lambda t: (manh(sx, sy, t[0], t[1]), t[1], t[0]))
        tx, ty = target
    else:
        tx, ty = ox, oy

    # Prefer immediate expansion toward target; add slight bias toward closing distance to opponent.
    best = (10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_to_target = manh(nx, ny, tx, ty)
        d_to_opp = manh(nx, ny, ox, oy)
        # Lower is better; tie-break deterministically by move order and coordinates.
        score = d_to_target * 10 + d_to_opp
        tie = (0 if (dx == 0 and dy == 0) else 1)
        cand = (score, -tie, (dx + 2) * 10 + (dy + 2))
        if cand < best:
            best = cand
            best_move = [dx, dy]

    return best_move if best else [0, 0]