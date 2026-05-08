def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = observation.get("self_role") or "pursuer"
    if role not in ("pursuer", "evader"):
        role = "pursuer"

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    curd = manh(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None

    # Deterministic tie-break order: iterate in fixed moves; compute scalar score.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = manh(nx, ny, ox, oy)
        ddelta = nd - curd

        mob = mobility(nx, ny)
        edge = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)

        # Primary objective depends on role
        if role == "pursuer":
            # minimize distance; also prefer higher mobility and avoid edges a bit
            score = (-nd) * 1000 + mob * 10 - edge * 3
        else:
            # maximize distance; avoid edges and prefer mobility to evade walls
            score = (nd) * 1000 + mob * 10 - edge * 30

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]