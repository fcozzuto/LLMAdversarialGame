def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # deterministic: fixed tie-break order via tuple sorting (score, -diag, -toward, stay_penalty)
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny)
        if nd == 0:
            return [dx, dy]
        adx = abs(nx - ox)
        ady = abs(ny - oy)
        sumd = adx + ady

        # Prefer diagonal, and prefer moves that reduce both components when possible.
        diag = 1 if (dx != 0 and dy != 0) else 0
        red_both = 1 if (adx < abs(sx - ox) and ady < abs(sy - oy)) else 0

        # Gentle penalty for staying still unless it doesn't worsen distance.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0

        # Primary: minimize Chebyshev distance; Secondary: minimize Manhattan; Tertiary: reduce both / diagonal.
        # Add a small bias to avoid moving that increases Manhattan distance.
        cur_sumd = abs(sx - ox) + abs(sy - oy)
        man_increase = 1 if sumd > cur_sumd else 0

        score = nd * 1000 + sumd * 2 + man_increase * 50 + stay_pen * 3 - red_both * 5 - diag * 1
        key = (score, -diag, -red_both, abs(nx - ox) + abs(ny - oy))
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]