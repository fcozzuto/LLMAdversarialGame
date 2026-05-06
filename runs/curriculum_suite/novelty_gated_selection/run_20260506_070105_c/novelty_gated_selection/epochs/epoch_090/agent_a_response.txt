def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy
    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    # Pick a resource where we have tempo (closer than opponent), but favor interior to avoid edge patrol.
    target = None
    best_key = (-10**18, 0)
    for rx, ry in resources:
        dm = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - dm  # positive if we are closer
        interior = edge_dist(rx, ry)  # higher = more interior
        # Prefer resources with positive advantage; also avoid very edge resources unless strongly favorable.
        key = (adv * 100 - dm + interior * 2, interior)
        if key > best_key:
            best_key = key
            target = (rx, ry)

    # If no resources, move to a stable interior point while keeping distance from opponent edge patrol.
    if target is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    # One-step lookahead greedy toward target; add penalties for moving onto edge near opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (not inb(nx, ny)) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        to_t = dist(nx, ny, tx, ty)
        to_o = dist(nx, ny, ox, oy)
        on_edge = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        opp_on_edge = 1 if (ox == 0 or oy == 0 or ox == w - 1 or oy == h - 1) else 0
        val = -to_t * 3 + to_o * 1 - on_edge * opp_on_edge * 2 - (abs(tx - nx) + abs(ty - ny) == 0) * 1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]