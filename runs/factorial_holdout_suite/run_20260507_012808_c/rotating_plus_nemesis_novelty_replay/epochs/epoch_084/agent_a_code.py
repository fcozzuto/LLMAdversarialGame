def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w - 1, 0
        if sx < tx: dx = 1
        elif sx > tx: dx = -1
        else: dx = 0
        if sy < ty: dy = 1
        elif sy > ty: dy = -1
        else: dy = 0
        return [dx, dy]

    resources.sort()
    best = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; slightly prioritize lower ds and higher do gap.
        key = (ds - (0.75 * do), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    curd = manh(sx, sy, rx, ry)
    best_move = (0, 0)
    best_newd = 10**9
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = manh(nx, ny, rx, ry)
        if nd < best_newd or (nd == best_newd and (dx, dy) < best_move) or (nd == best_newd and dx == 0 and dy == 0 and best_move != (0, 0)):
            if nd <= curd + 1:
                best_newd = nd
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]