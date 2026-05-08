def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_pursuer = any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y, tx, ty):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx >= dy else dy

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    # Deterministic corner target for evader: farthest corner from opponent.
    best_corner = corners[0]
    best_corner_dist = -1
    for c in corners:
        d = cheb(ox, oy, c[0], c[1])
        if d > best_corner_dist:
            best_corner_dist = d
            best_corner = c

    # Evaluate all legal moves and pick best deterministically.
    best_score = None
    best_move = (0, 0)
    tie = 0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if i_am_pursuer:
            # Pursuer: minimize distance; also prefer moving "around" obstacles via corner alignment.
            dist = cheb(nx, ny, ox, oy)
            corner_align = min(cheb(nx, ny, cx, cy) for (cx, cy) in corners)
            score = -dist - 0.03 * corner_align
        else:
            # Evader: maximize distance from pursuer; keep drifting to a chosen corner.
            dist = cheb(nx, ny, ox, oy)
            corner_dist = cheb(nx, ny, best_corner[0], best_corner[1])
            # Prefer also staying away from the center a bit (helps cornering on empty maps).
            center_dist = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
            score = dist + 0.06 * corner_dist + 0.02 * center_dist
        if best_score is None or score > best_score or (score == best_score and tie < 1e-9):
            best_score = score
            best_move = (dx, dy)
            tie = 0
        # deterministic tie-break: first in fixed move order already wins; we do nothing else

    return [int(best_move[0]), int(best_move[1])]