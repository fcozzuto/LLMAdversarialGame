def choose_move(observation):
    gw = observation.get("grid_width", 8) or 8
    gh = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if resources:
            closest = None
            for r in resources:
                rx, ry = int(r[0]), int(r[1])
                d = dist2(nx, ny, rx, ry)
                if closest is None or d < closest:
                    closest = d
            d_o = dist2(nx, ny, ox, oy)
            sc = (closest, -d_o, abs(dx) + abs(dy))
        else:
            d_o = dist2(nx, ny, ox, oy)
            sc = (-d_o, abs(dx) + abs(dy))
        if best is None or sc < best[0]:
            best = (sc, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]