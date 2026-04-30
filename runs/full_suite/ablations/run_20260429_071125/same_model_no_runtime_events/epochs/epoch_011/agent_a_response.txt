def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, dict):
            pos = r.get("pos", None)
            if pos and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
                continue
            if "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)
            if best is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def best_resource_for(posx, posy):
        # prefer resources closer than opponent; then closest to us; then farthest from opponent
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(posx, posy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds
            key = (margin, -ds, do, rx, ry)
            if best is None or key > best_key:
                best_key = key
                best = (rx, ry, ds, do)
        return best

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        rx, ry, ds, do = best_resource_for(nx, ny)

        # local safety: nudge away if opponent is very close
        opp_close = cheb(nx, ny, ox, oy)
        safety = opp_close
        # obstacle proximity penalty (discourages walking into clutter)
        adj_block = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            px, py = nx + adx, ny + ady
            if (px, py) in obstacles:
                adj_block += 1

        # value: maximize advantage over opponent on targeted resource; minimize our distance
        margin = do - ds
        val = 3.0 * margin - 1.2 * ds + 0.25 * safety - 0.4 * adj_block
        # if both are about equally close, spread out a bit
        if margin <= 0:
            val += 0