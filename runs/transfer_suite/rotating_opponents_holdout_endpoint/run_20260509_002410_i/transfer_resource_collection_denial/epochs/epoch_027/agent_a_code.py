def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = -(mdist(nx, ny, tx, ty))
            if best is None or v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    scored = []
    for x, y in resources:
        sd = mdist(sx, sy, x, y)
        od = mdist(ox, oy, x, y)
        advantage = od - sd  # positive means we reach first (or at least sooner)
        # Prefer winning resources; then prefer closer by our distance.
        scored.append((advantage, -sd, -x, -y, x, y))
    scored.sort(reverse=True)
    best_adv = scored[0][0]
    contenders = [s for s in scored if s[0] >= best_adv]
    # Deterministic: pick the first contender (sorted order already deterministic).
    _, _, _, _, tx, ty = contenders[0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal move is blocked, fall back deterministically to single-axis steps.
    cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for ddx, ddy in cand:
        nx, ny = sx + ddx, sy + ddy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [ddx, ddy]
    return [0, 0]