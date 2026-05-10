def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    want_close = (("pursuer" in role) or ("chaser" in role) or ("hunter" in role) or ("interceptor" in role) or ("catch" in role))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        score = d if want_close else -d

        if nx == ox and ny == oy:
            return [dx, dy]

        # Tie-break deterministically: prefer moves that maximize local mobility (for escape) or reduce it slightly (for chase)
        mobility = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if free(tx, ty):
                mobility += 1
        score = score + (0.001 * (mobility if not want_close else -mobility))

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move