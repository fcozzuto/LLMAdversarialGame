def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        dx = dx if dx >= 0 else -dx
        dy = dy if dy >= 0 else -dy
        m = dx if dx >= dy else dy
        return m * m

    # Deterministic target bias: evader -> farthest corner; pursuer -> nearest corner to enemy (to cut off)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: cheb2(c[0], c[1], ox, oy))
    else:
        tx, ty = min(corners, key=lambda c: cheb2(c[0], c[1], ox, oy))

    best_move = [0, 0]
    best_val = None
    best_tie = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_opp2 = cheb2(nx, ny, ox, oy)
        # Additional bias toward/away from a corner depending on role
        dist_corner2 = cheb2(nx, ny, tx, ty)

        if is_evader:
            # prioritize staying far from opponent; secondary: move away from corner (i.e., not approaching it too fast)
            val = dist_opp2 * 1000 - dist_corner2
        else:
            # prioritize moving closer to opponent; secondary: move toward a corner associated with cutting off
            val = -dist_opp2 * 1000 - dist_corner2

        tie = (dx, dy)
        if best_val is None:
            best_val, best_tie, best_move = val, tie, [dx, dy]
        else:
            if is_evader:
                if val > best_val or (val == best_val and tie < best_tie):
                    best_val, best_tie, best_move = val, tie, [dx, dy]
            else:
                if val > best_val or (val == best_val and tie < best_tie):
                    best_val, best_tie, best_move = val, tie, [dx, dy]

    return [int(best_move[0]), int(best_move[1])]