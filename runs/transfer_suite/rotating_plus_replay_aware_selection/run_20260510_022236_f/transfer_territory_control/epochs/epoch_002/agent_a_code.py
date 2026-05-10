def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", [])
    obs = set((int(p[0]), int(p[1])) for p in obstacles if len(p) >= 2)

    un = observation.get("unclaimed_cells", None)
    if un is None:
        un = observation.get("unclaimed", [])
    un_set = set((int(p[0]), int(p[1])) for p in un if len(p) >= 2)

    res = observation.get("resources", [])
    res_set = set((int(p[0]), int(p[1])) for p in res if len(p) >= 2)

    self_cnt = len(observation.get("self_territory", [])) if observation.get("self_territory", None) is not None else observation.get("self_territory_count", 0)
    opp_cnt = len(observation.get("opponent_territory", [])) if observation.get("opponent_territory", None) is not None else observation.get("opponent_territory_count", 0)
    behind = 1 if self_cnt <= opp_cnt else -1  # if behind, go toward opponent; else away

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    bx = by = 0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        toward = cheb(nx, ny, ox, oy)
        # Score: prefer unclaimed adjacent; if resource, strong; then pressure objective
        is_un = 1 if (nx, ny) in un_set else 0
        is_res = 1 if (nx, ny) in res_set else 0
        # When behind: minimize distance to opponent; when ahead: maximize
        press = toward * behind
        score = is_res * 100000 + is_un * 10000 + press
        if best is None or score > best:
            best = score
            bx, by = dx, dy

    if best is None:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [bx, by]