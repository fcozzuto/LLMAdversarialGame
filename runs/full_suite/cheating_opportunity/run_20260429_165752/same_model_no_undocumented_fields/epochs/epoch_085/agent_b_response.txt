def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_t = resources[0]
        best_score = None
        for (rx, ry) in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = ds - do  # smaller is better for us
            if best_score is None or adv < best_score or (adv == best_score and (rx, ry) < best_t):
                best_score = adv
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    opp_to_target = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dnew = cheb(nx, ny, tx, ty)
        dcur = cheb(sx, sy, tx, ty)
        move_towards = dnew < dcur
        # Deny if opponent is close: prioritize staying in front (not necessarily reaching).
        deny = (opp_to_target <= 2) * (dnew - max(0, opp_to_target - 1))
        val = (-dnew) + (2.0 if move_towards else 0.0) - 0.15 * deny
        if best_val is None or val > best_val or (val == best_val and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]