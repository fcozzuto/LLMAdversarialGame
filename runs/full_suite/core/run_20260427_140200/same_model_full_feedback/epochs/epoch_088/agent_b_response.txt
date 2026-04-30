def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_val = -10**18
    best_move = (0, 0)
    res_sorted = sorted(resources, key=lambda r: (r[0], r[1]))

    def nearest_to(px, py):
        md = 10**9
        target = res_sorted[0]
        for rx, ry in res_sorted:
            d = cheb(px, py, rx, ry)
            if d < md:
                md = d
                target = (rx, ry)
        return md, target

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self, tgt = nearest_to(nx, ny)
        tx, ty = tgt
        d_opp = cheb(ox, oy, tx, ty)
        d_opp_now = cheb(ox, oy, nx, ny)
        # Favor getting closer to a target, and when we're closer than opponent, lean in.
        # Also avoid moving into immediate opponent proximity.
        val = -d_self
        val += 0.5 * (d_opp - d_self)  # higher if opponent is farther from the target
        if d_opp <= d_self:
            val -= 0.8  # likely opponent can contest
        val -= 0.15 * d_opp_now  # stay away from opponent
        # Prefer deterministic tie-break: lexicographic move by (dx,dy)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]