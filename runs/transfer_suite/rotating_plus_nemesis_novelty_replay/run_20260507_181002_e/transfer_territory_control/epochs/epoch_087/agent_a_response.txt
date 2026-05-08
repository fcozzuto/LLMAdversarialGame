def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def man(a, b, c, d): return abs(a - c) + abs(b - d)
    def dist_center(x, y):
        dx, dy = x - cx, y - cy
        return (dx * dx + dy * dy) ** 0.5
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    curr_opp = man(sx, sy, ox, oy)
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            sc = -1000
        else:
            sc = 0
            if (nx, ny) in selfT:
                sc += 6
            elif (nx, ny) in oppT:
                sc += 12
                sc += 0.4 * (curr_opp - man(nx, ny, ox, oy))  # closer to opponent frontier is good
                sc += 1.5 * (dist_center(nx, ny) - dist_center(sx, sy))  # favor central pressure
            elif (nx, ny) in unclaimed:
                sc += 22
                sc += 0.8 * (curr_opp - man(nx, ny, ox, oy))  # avoid letting opponent surround you
                sc += 1.2 * dist_center(nx, ny)               # claim toward center (opponent does this)
            else:
                sc -= 2
            if man(nx, ny, ox, oy) <= curr_opp:
                sc += 0.8  # slight bias toward improving distance when safe

        if sc > best_score:
            best_score = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]