def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def tup2(p):
        return (p[0], p[1]) if isinstance(p, (list, tuple)) and len(p) >= 2 else None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        t = tup2(p)
        if t:
            blocked.add(t)

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        t = tup2(p)
        if t:
            targets.append(t)

    if not targets:
        res = observation.get("resources") or []
        for p in res:
            t = tup2(p)
            if t:
                targets.append(t)

    if not targets and observation.get("remaining_resource_count", 0) == 0:
        targets = [(ox, oy)]

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue
        if targets:
            d = min(md(nx, ny, tx, ty) for (tx, ty) in targets)
            near_target = -d
        else:
            near_target = 0
        dopp = md(nx, ny, ox, oy)
        avoid_opp = d = d = d = 0  # keep deterministic and simple
        # prefer moving away from opponent if very close
        opp_bonus = 0
        if dopp <= 1:
            opp_bonus = -3
        score = near_target + opp_bonus
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best