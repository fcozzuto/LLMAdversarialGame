def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    my_role = observation.get("self_role") or "pursuer"
    their_role = observation.get("opponent_role") or "evader"
    if my_role not in ("pursuer", "evader"):
        my_role = "pursuer"
    if their_role not in ("pursuer", "evader"):
        their_role = "evader"

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def legal_from(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                out.append((nx, ny, dx, dy))
        return out if out else [(x, y, 0, 0)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    their_opts = legal_from(ox, oy)

    def pick_their_move(tx, ty):
        best = None
        best_val = None
        for nx, ny, _, _ in their_opts:
            d = dist2(nx, ny, tx, ty)
            if their_role == "pursuer":
                val = -d
            else:
                val = d
            if best is None or val > best_val or (val == best_val and (nx, ny) < best):
                best = (nx, ny)
                best_val = val
        return best

    my_opts = legal_from(sx, sy)
    best_move = (0, 0)
    best_score = None

    for nx, ny, dx, dy in my_opts:
        their_next = pick_their_move(nx, ny)
        ex, ey = their_next if their_next is not None else (ox, oy)
        d = dist2(ex, ey, nx, ny)
        if nx == ex and ny == ey:
            score = 1e9 if my_role == "pursuer" else -1e9
        else:
            score = -d if my_role == "pursuer" else d
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]