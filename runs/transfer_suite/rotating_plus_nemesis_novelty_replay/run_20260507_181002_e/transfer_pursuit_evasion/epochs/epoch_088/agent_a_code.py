def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obs.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = "evad" in role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def obst_adj(x, y):
        c = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in obs:
                c += 1
        return c

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        # Primary: evader maximizes distance, pursuer minimizes distance
        val = d if evader else -d
        # Tie-break: prefer fewer adjacent obstacles, then deterministic lexicographic by (dx,dy)
        t = (-obst_adj(nx, ny), dx, dy)
        key = (val, t)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]