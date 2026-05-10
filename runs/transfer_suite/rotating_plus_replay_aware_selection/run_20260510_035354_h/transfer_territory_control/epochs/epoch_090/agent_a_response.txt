def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    self_territory = observation.get("self_territory") or []
    opp_territory = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    ax, ay = int(ax), int(ay)

    def toset(lst):
        s = set()
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obset = toset(obstacles)
    uset = toset(self_territory)
    oset = toset(opp_territory)
    ucell = toset(unclaimed)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)

    opp_cells = list(oset)
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue
        score = 0
        if (nx, ny) in ucell:
            score += 12000
        if (nx, ny) in oset:
            score += 6000  # flipping opponent-owned cell helps us
        if (nx, ny) in uset:
            score += 0

        edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        score += edge * 25
        dist_center = abs(nx - cx) + abs(ny - cy)
        score -= dist_center * 20

        if opp_cells:
            dmin = min(abs(nx - ox) + abs(ny - oy) for ox, oy in opp_cells)
            score += dmin * 6  # prefer moving away from central opponent expansion
        else:
            score += 50

        # deterministic tie-break: later moves won't win if same score
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]