def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def opp_neighbors(x, y):
        res = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if free(nx, ny):
                    res.append((nx, ny))
        return res

    best_dx, best_dy = 0, 0
    best_score = None

    # Deterministic tie-breaking: later candidates only if strictly better.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            # engine would keep us in place; treat as such
            nx, ny = sx, sy
            dx, dy = 0, 0

        d_to_opp = dist2(nx, ny, ox, oy)

        # Trap heuristic: penalize moves that give opponent many options increasing distance from us.
        trap = 0
        for px, py in opp_neighbors(ox, oy):
            if dist2(px, py, nx, ny) >= dist2(ox, oy, nx, ny):
                trap += 1

        # Primary: get closer (min d_to_opp). Secondary: reduce opponent options (min trap). Tertiary: prefer progress in x, then y.
        score = (d_to_opp, trap, -(nx - sx), -(ny - sy))
        if best_score is None or score < best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]