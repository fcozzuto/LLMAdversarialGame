def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    turn = int(observation.get("turn_index", 0))
    phase = 0 if (turn % 4) < 2 else 1  # alternate: growth vs pressure

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base: keep toward center a bit, but not at expense of expansion/pressure.
        score = -0.35 * (((nx - cx) ** 2 + (ny - cy) ** 2) ** 0.5)

        # Prefer stepping into opponent territory (flipping on entry).
        if (nx, ny) in opT:
            score += 40.0

        # Prefer stepping into unclaimed.
        if (nx, ny) in unT:
            score += 18.0

        # If moving closer to opponent and pressure mode, add more.
        if phase == 1:
            score += 2.0 * (man(nx, ny, ox, oy) <= man(sx, sy, ox, oy))

        # Frontier bonus: moving adjacent to unclaimed cells increases expansion potential.
        adj_un = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and ((tx, ty) in unT):
                adj_un += 1
        score += 2.8 * adj_un

        # Discourage immediate retreat when not beneficial.
        if (nx, ny) in selfT:
            score -= 1.0

        # Tie-break deterministically toward x then y.
        candidates.append((score, nx, ny))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    best = candidates[0]
    dx, dy = best[1] - sx, best[2] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]