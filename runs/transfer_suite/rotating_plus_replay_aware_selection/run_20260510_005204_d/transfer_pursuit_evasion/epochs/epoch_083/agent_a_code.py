def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def free_count(x, y):
        c = 0
        for ax, ay in moves:
            tx, ty = x + ax, y + ay
            if inb(tx, ty) and (tx, ty) not in blocked:
                c += 1
        return c

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d = dist2(nx, ny, ox, oy)
        loc = dist2(nx, ny, cx, cy) * 0.001

        # local mobility: prefer moves that keep options open (helps both roles)
        mob = -free_count(nx, ny) if is_evader else -free_count(nx, ny)
        # For pursuer, lower mobility is bad (trapped). For evader, slightly penalize low mobility too.
        trap_pen = (5 - free_count(nx, ny)) * (0.15 if free_count(nx, ny) < 5 else 0.0)

        score = 0.0
        if is_evader:
            score = (d * 1.0) - loc + mob * 0.02 - trap_pen
        else:
            score = (-d * 1.0) - loc + mob * 0.02 - trap_pen

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]