def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def free_count(x, y):
        c = 0
        for adx, ady in moves:
            nx, ny = x + adx, y + ady
            if inb(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    def wall_score(x, y):
        # Prefer staying away from obstacles
        s = 0
        for bx, by in blocked:
            d = dist2(x, y, bx, by)
            if d == 0:
                return -10**9
            if d <= 4:
                s -= (5 - d) * 20
        return s

    best = None
    bestv = -10**18 if is_evader else -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d2 = dist2(nx, ny, ox, oy)
        fcnt = free_count(nx, ny)
        ws = wall_score(nx, ny)

        if is_evader:
            # maximize distance, avoid getting stuck
            score = d2 * 10 + fcnt * 3 + ws
        else:
            # minimize distance, avoid dead-ends
            score = (-d2) * 10 + fcnt * 3 + ws

        # Deterministic tie-break via lexical move order in moves list
        if best is None or score > bestv:
            bestv = score
            best = (dx, dy)

    return [0, 0] if best is None else [int(best[0]), int(best[1])]