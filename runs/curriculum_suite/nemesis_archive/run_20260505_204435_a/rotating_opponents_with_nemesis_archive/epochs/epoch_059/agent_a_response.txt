def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(p):
        if isinstance(p, dict):
            q = p.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
            return None
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return (p[0], p[1])
        return None

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)

    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        best_adv = -10**9
        best_td = 10**9
        for rx, ry in rpos:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            if self_d == 0:
                adv = 999999
            else:
                adv = (opp_d - self_d)
            # prefer decisive advantage; break ties toward closer capture
            if adv > best_adv or (adv == best_adv and self_d < best_td):
                best_adv = adv
                best_td = self_d

        # small penalty for moving away from globally close resources
        near_self = min(md(nx, ny, rx, ry) for rx, ry in rpos)
        # small tie-break using coordinates (deterministic)
        tie = (nx * 9 + ny)
        val = (best_adv * 1000) - (near_self * 3) - tie * 0.0001
        if best is None or val > best[0]:
            best = (val, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]