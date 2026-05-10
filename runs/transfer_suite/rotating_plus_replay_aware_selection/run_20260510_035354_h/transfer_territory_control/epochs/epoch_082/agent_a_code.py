def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def get_xy(key, default=(0, 0)):
        v = observation.get(key, default)
        try:
            if isinstance(v, (list, tuple)) and len(v) >= 2:
                x = int(v[0]); y = int(v[1])
                return (x, y)
        except Exception:
            pass
        return default

    ax, ay = get_xy("self_position", (0, 0))
    bx, by = get_xy("opponent_position", (0, 0))

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            try:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x = int(p[0]); y = int(p[1])
                    if 0 <= x < w and 0 <= y < h:
                        s.add((x, y))
            except Exception:
                pass
        return s

    unclaimed = toset(observation.get("unclaimed_cells") or [])
    obstacles = toset(observation.get("obstacles") or [])
    opp_terr = toset(observation.get("opponent_territory") or [])
    self_terr = toset(observation.get("self_territory") or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    targets = []
    if opp_terr:
        for x, y in opp_terr:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in unclaimed:
                        targets.append((nx, ny))
    if not targets:
        targets = list(unclaimed) if unclaimed else [(bx, by)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = moves[4]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if targets:
            tx, ty = targets[0]
            dmin = 10**18
            for t in targets:
                dd = abs(t[0] - nx) + abs(t[1] - ny)
                if dd < dmin:
                    dmin = dd
                    tx, ty = t
            score = -dmin
            if (nx, ny) in unclaimed:
                score += 1000
            if (nx, ny) in self_terr:
                score -= 10
            if (nx, ny) == (bx, by):
                score += 50
            if (nx, ny) in opp_terr:
                score += 200
        else:
            score = 0
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]