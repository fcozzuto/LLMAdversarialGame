def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    ti = int(observation.get("turn_index", 0) or 0)

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best = None
        for tx, ty in resources:
            ds = dist(sx, sy, tx, ty)
            do = dist(ox, oy, tx, ty)
            # Prefer resources where we can arrive sooner; if equal, prefer closer one.
            # Small deterministic tie-break from position/turn.
            adv = (do - ds)
            key = (-(adv), ds, ((tx * 31 + ty * 17 + sx * 7 + sy * 13 + ti) % 10))
            if best is None or key < best[0]:
                best = (key, tx, ty)
        tx, ty = best[1], best[2]
    else:
        tx, ty = int((w - 1) / 2), int((h - 1) / 2)

    best_move = (10**9, 0, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            dnew = dist(nx, ny, tx, ty)
            # If we can, also reduce opponent distance to our target (denial pressure).
            do_new = dist(ox, oy, tx, ty)
            tie = ((nx * 23 + ny * 29 + ti) % 7)
            key = (dnew, -do_new, tie)
            if key < best_move[0:3]:
                best_move = (key[0], dx, dy, key[2])

    return [int(best_move[1]), int(best_move[2])]