def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def blocked(x, y):
        return (x, y) in obs

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            return [0, 0]
        return [dx, dy]

    best_rx = best_ry = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        lead = od - sd  # positive means we can arrive first
        tie = (rx * 131 + ry * 17) % 997
        # Strongly prefer winning captures; next prefer smaller remaining time.
        key = (-lead, sd, tie) if lead > 0 else (-lead, sd + 2 * max(0, -lead), tie)
        if best_key is None or key < best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    contested = (man(sx, sy, best_rx, best_ry) >= man(ox, oy, best_rx, best_ry))

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d_self = man(nx, ny, best_rx, best_ry)
        d_opp = man(nx, ny, ox, oy)
        # If contested, add opponent separation; otherwise just race the target.
        score = d_self + (2 if contested else 0) * (-d_opp)
        score = score * 1000 + (0 if dx == 0 and dy == 0 else 1)  # prefer moving
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move