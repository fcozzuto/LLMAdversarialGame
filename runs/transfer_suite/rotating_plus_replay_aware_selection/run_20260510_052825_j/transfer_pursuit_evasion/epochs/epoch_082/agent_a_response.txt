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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role) or ("hunter" in role) or (not evader)

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    obstacles = list(blocked)
    def obs_pen(nx, ny):
        if not obstacles:
            return 0
        md = 10**9
        for x, y in obstacles:
            dd = dist2(nx, ny, x, y)
            if dd < md:
                md = dd
        # Penalize being close to obstacles; keep deterministic scaling.
        return -md

    def edge_pen(nx, ny):
        # Encourage staying away from borders for evader; no-op for pursuer.
        if not (0 <= nx < w and 0 <= ny < h):
            return 0
        d = min(nx, ny, w - 1 - nx, h - 1 - ny)
        return d

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        pen = obs_pen(nx, ny)
        e = edge_pen(nx, ny)

        # If pursuer: minimize distance (primary). If evader: maximize distance (primary).
        if pursuer and not evader:
            key = (d, -pen, -e, abs(dx), abs(dy), dx, dy)
        else:
            key = (-d, -pen, e, -abs(dx), -abs(dy), -dx, -dy)

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]