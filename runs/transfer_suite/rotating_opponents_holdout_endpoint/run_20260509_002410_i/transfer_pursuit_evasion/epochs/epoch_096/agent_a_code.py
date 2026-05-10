def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or (role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obs(x, y):
        n = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    n += 1
        return n

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # choose a fixed evasion corner preference based on opponent quadrant
    idx = (0 if ox < w // 2 else 1) * 2 + (0 if oy >= h // 2 else 1)
    ev_corner = corners[idx % 4]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        if (nx, ny) in obstacles:
            score = -10**9 if is_pursuer else 10**9
        else:
            dist = cheb(nx, ny, ox, oy)
            nobs = near_obs(nx, ny)
            # deterministic corner bias for evader
            corner_bias = cheb(nx, ny, ev_corner[0], ev_corner[1])
            if is_pursuer:
                score = -(dist * 10 + nobs * 3) - (corner_bias * 0.05)
            else:
                score = (dist * 10 - nobs * 3) + (corner_bias * 0.1)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]