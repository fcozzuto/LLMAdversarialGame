def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    mode = "evade" if "evader" in self_role else "pursue"

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best = None
    best_sc = None
    cur_d2 = dist2(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d2_new = dist2(nx, ny, ox, oy)
        man_new = abs(nx - ox) + abs(ny - oy)
        man_cur = abs(sx - ox) + abs(sy - oy)

        if mode == "evade":
            # Prefer increasing distance; also prefer moving toward the farthest corner.
            tx, ty = far_corner
            corner_d2 = dist2(nx, ny, tx, ty)
            corner_d2_cur = dist2(sx, sy, tx, ty)
            sc = 10.0 * (d2_new - cur_d2) + 0.8 * corner_d2 + 0.3 * (corner_d2 - corner_d2_cur)
            # Small deterministic tie-break: slightly prefer not to get closer in Manhattan.
            sc += 0.15 * (man_cur - man_new)
        else:
            # Pursuer: minimize distance and avoid stepping away from near_corner (helps interception).
            tx, ty = near_corner
            corner_d2 = dist2(nx, ny, tx, ty)
            corner_d2_cur = dist2(sx, sy, tx, ty)
            sc = -10.0 * (d2_new) - 0.2 * man_new - 0.3 * (corner_d2 - corner_d2_cur)

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]