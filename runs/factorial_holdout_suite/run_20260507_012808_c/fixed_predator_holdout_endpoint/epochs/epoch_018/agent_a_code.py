def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                res.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not res:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sc = dist(nx, ny, ox, oy)
            if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < best[1]):
                best = (sc, (dx, dy))
        return [best[1][0], best[1][1]]

    # Pick move that maximizes expected resource advantage: (opp_dist - self_dist),
    # with a slight preference for smaller self_dist to finish routes faster.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_adv = None
        for rx, ry in res:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd
            # Encourage immediate collection (sd==0) deterministically.
            if best_adv is None or adv > best_adv[0] or (adv == best_adv[0] and (sd < best_adv[1] or (sd == best_adv[1] and (rx, ry) < best_adv[2]))):
                best_adv = (adv, sd, (rx, ry))
        # Tie-break: higher advantage, then smaller self distance, then prefer diagonal/forward deterministically.
        key = (best_adv[0], -best_adv[1], -abs(dx) - abs(dy), -dx, -dy, dx, dy)
        if best is None or key > best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]]