def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    role = str(observation.get("self_role", "") or "").lower()
    self_is_evader = "evader" in role

    def edge_potential(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    best_score = None
    best_move = [0, 0]
    cur_d = manh(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        nd = manh(nx, ny, ox, oy)

        # Pursuer: reduce distance and move toward board edges (limit escape paths).
        # Evader: increase distance and avoid edges if that would trap movement (use edge depth + mobility).
        if not self_is_evader:
            score = (cur_d - nd) * 10.0 - (edge_potential(nx, ny)) * 0.6 + mobility(nx, ny) * 0.1 - nd * 0.3
        else:
            score = (nd - cur_d) * 10.0 + (edge_potential(nx, ny)) * 0.6 + mobility(nx, ny) * 0.4 - nd * 0.05

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move