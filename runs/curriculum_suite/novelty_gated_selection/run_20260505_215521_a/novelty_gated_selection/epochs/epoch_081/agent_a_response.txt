def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources: run to increase separation from opponent.
    if not resources:
        best = None
        for dx, dy in sorted(moves):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            d = cheb(nx, ny, ox, oy)
            val = (d, -dx, -dy)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [0, 0] if best is None else [best[1], best[2]]

    # Choose a resource target, then choose a step that maximizes our advantage over opponent.
    # Advantage = (opp_dist - our_dist) with a small bias to faster arrival.
    chosen = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Prefer targets we can reach earlier and/or are closer than opponent.
        val = (d_opp - d_self, -(d_self), -(abs(rx - sx) + abs(ry - sy)), rx, ry)
        if chosen is None or val > chosen[0]:
            chosen = (val, rx, ry)
    _, tx, ty = chosen

    best = None
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        our_now = cheb(nx, ny, tx, ty)
        opp_now = cheb(ox, oy, tx, ty)
        # Also add a deterrent: avoid moving closer to opponent in general.
        sep = cheb(nx, ny, ox, oy)

        # Heuristic: keep maximizing our arrival advantage; if tied, increase separation.
        advantage = (opp_now - our_now)
        val = (advantage, -our_now, sep, -(abs(nx - tx) + abs(ny - ty)), -dx, -dy)
        if best is None or val > best[0]:
            best = (val, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]