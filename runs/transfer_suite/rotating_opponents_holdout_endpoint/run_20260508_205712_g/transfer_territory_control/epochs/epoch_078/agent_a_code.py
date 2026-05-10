def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        base = 0.0
        if (x, y) in oppT:
            base += 8.0
        elif (x, y) in unclaimed:
            base += 6.0
        elif (x, y) in selfT:
            base += 2.5
        else:
            base += 1.0

        d_op = abs(x - ox) + abs(y - oy)
        base += 0.18 * d_op  # spread away from opponent unless contesting

        d_center = abs(x - cx) + abs(y - cy)
        base += 0.06 * d_center  # deny center-claim style by pushing outward

        if obstacles:
            best = 10**9
            for bx, by in obstacles:
                best = min(best, abs(x - bx) + abs(y - by))
            base += 0.12 * min(best, 6)  # prefer safer cells near free space
        return base

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            candidates.append((-10**9, dx, dy))
        else:
            candidates.append((score_cell(nx, ny), dx, dy))

    candidates.sort(key=lambda t: (t[0], -abs(t[1]) - abs(t[2]), t[1], t[2]), reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]