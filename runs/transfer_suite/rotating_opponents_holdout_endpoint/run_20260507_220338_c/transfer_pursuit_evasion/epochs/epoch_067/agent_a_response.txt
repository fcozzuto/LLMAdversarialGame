def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    self_is_evader = ("evader" in role_s) or ("runner" in role_s) or ("flee" in role_s) or ("avoid" in role_s)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def near_block_cost(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in blocked:
                    c += 1
        return c

    best = None
    best_score = None

    # Tie-break preference: move that continues the general direction to/from opponent.
    dir_x = 0 if ox == sx else (1 if ox > sx else -1)
    dir_y = 0 if oy == sy else (1 if oy > sy else -1)
    want_dx = dir_x if not self_is_evader else -dir_x
    want_dy = dir_y if not self_is_evader else -dir_y

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        dist = cheb(nx, ny, ox, oy)
        # Pursuer: minimize distance; Evader: maximize distance.
        primary = dist if self_is_evader else -dist

        # Avoid stepping into obstacle pockets and avoid edges that can trap.
        pocket = near_block_cost(nx, ny)
        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)

        # Anti-oscillation via local direction alignment.
        align = 0
        if dx == want_dx:
            align += 1
        if dy == want_dy:
            align += 1
        # Discourage staying if not optimal.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0

        score = primary - 0.35 * pocket - (0.15 if edge else 0) + 0.08 * align - 0.25 * stay_pen

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]