def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    best = (None, -10**9)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_next = md(nx, ny, ox, oy)
        opp_next = md(ox, oy, nx, ny)  # proxy for opponent pressure
        # Nearest resource distance after move
        our_res = 10**9
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if d < our_res:
                our_res = d
        # If we land on a resource, it's best
        res_pick = 1 if (nx, ny) in resources else 0
        # Prefer moves that make us relatively closer to resources than opponent (by proxy).
        opp_res = 10**9
        for rx, ry in resources:
            d = md(ox, oy, rx, ry)
            if d < opp_res:
                opp_res = d
        score = 50 * res_pick + (opp_res - our_res) + 0.05 * (our_next - opp_next)
        # Deterministic tie-break: smaller (dx,dy) lexicographically after sorting
        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]