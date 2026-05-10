def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    self_t = set(map(tuple, observation.get("self_territory", []) or []))
    opp_t = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def center_score(x, y):
        # higher is better; closer to center preferred for territory edge play
        return -abs(x - cx) - abs(y - cy)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Base: claim/flip value
        if (nx, ny) in self_t:
            base = 1.0
        elif (nx, ny) in opp_t:
            base = 6.0
        else:
            base = 3.0  # unclaimed or unknown

        # Pressure: move away from opponent to create edge barriers
        d_opp = dist(nx, ny, ox, oy)
        safety = d_opp * 0.35

        # Momentum: prefer expanding into open space
        free_neighbors = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    free_neighbors += 1
        mobility = free_neighbors * 0.12

        # Slight pull toward center and away from staying in place
        move_penalty = 0.08 if (dx == 0 and dy == 0) else 0.0

        score = base + safety + mobility + center_score(nx, ny) - move_penalty
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]