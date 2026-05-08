def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = observation.get("self_role") or "pursuer"
    if role not in ("pursuer", "evader"):
        role = "pursuer"

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def legal_from(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                out.append((nx, ny, dx, dy))
        if not out:
            return [(x, y, 0, 0)]
        return out

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    my_opts = legal_from(sx, sy)
    their_opts = legal_from(ox, oy)

    best = None
    best_val = None
    for nx, ny, dx, dy in my_opts:
        if role == "pursuer":
            worst_dist = -1
            for tx, ty, _, _ in their_opts:
                d = dist2(nx, ny, tx, ty)
                if d > worst_dist:
                    worst_dist = d
            val = -worst_dist
        else:  # evader
            best_dist = 10**9
            for tx, ty, _, _ in their_opts:
                d = dist2(nx, ny, tx, ty)
                if d < best_dist:
                    best_dist = d
            val = best_dist

        # tie-break: prefer higher mobility
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            def mobility(x, y):
                c = 0
                for ddx, ddy in moves:
                    if inb(x + ddx, y + ddy):
                        c += 1
                return c
            if mobility(nx, ny) > mobility(sx, sy):
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]