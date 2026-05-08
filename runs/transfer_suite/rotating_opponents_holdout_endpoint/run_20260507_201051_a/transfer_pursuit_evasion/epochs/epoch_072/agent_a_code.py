def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    orr = str(observation.get("opponent_role") or "").lower()
    is_pursuer = ("pursu" in sr) or ("hunter" in sr)
    if "evasion" in str(observation.get("environment_name", "")).lower():
        if ("evad" in sr) or ("escape" in sr) or ("runner" in sr):
            is_pursuer = False
    if ("pursu" in orr) or ("hunter" in orr):
        is_pursuer = False
    if ("evad" in orr) or ("escape" in orr) or ("runner" in orr):
        is_pursuer = True

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        if is_pursuer:
            # minimize distance; also try not to waste steps (prefer decreasing distance)
            dec = cheb(sx, sy, ox, oy) - d
            score = -10 * d + 3 * dec
            # bias toward blocking: avoid moving closer to the farthest corner from opponent
            score -= 0.05 * cheb(nx, ny, far_corner[0], far_corner[1])
        else:
            # maximize distance; drift toward the farthest corner relative to opponent
            score = 10 * d
            score += 0.02 * cheb(nx, ny, far_corner[0], far_corner[1])
            score -= 0.01 * cheb(nx, ny, near_corner[0], near_corner[1])

        # deterministic tie-break: smallest (dx,dy) in lexical order after score tie
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]