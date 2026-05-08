def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Farthest corner from opponent (evader target); nearest corner otherwise (pursuer tie-break)
    best_corner = None
    best_cd2 = None
    for cx, cy in corners:
        cd2 = dist2(cx, cy, ox, oy)
        if best_corner is None or (evader and cd2 > best_cd2) or ((not evader) and cd2 < best_cd2):
            best_corner, best_cd2 = (cx, cy), cd2

    # Precompute obstacle "clearance" for tie-breaking
    obst_list = list(obst)

    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_op = dist2(nx, ny, ox, oy)
        if evader:
            # Primary: maximize distance from pursuer. Secondary: get toward farthest corner. Tertiary: stay clear of obstacles.
            d_corner = dist2(nx, ny, best_corner[0], best_corner[1])
            min_obst = 10**9
            for ex, ey in obst_list:
                dd = dist2(nx, ny, ex, ey)
                if dd < min_obst:
                    min_obst = dd
            score = (d_op, -d_corner, min_obst)
        else:
            # Pursuer: minimize distance to evader; also prefer corners that worsen evader options (tie-break toward opponent's farthest corner).
            d_corner = dist2(nx, ny, best_corner[0], best_corner[1])
            score = (-d_op, d_corner)

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]