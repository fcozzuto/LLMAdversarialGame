def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def kingdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for x, y in resources:
        our_t = kingdist(sx, sy, x, y)
        opp_t = kingdist(ox, oy, x, y)
        lead = opp_t - our_t  # positive => we arrive earlier
        key = (-(lead > 0), -lead, our_t, x, y)  # prioritize guaranteed lead, then max lead
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        cand.append((kingdist(nx, ny, tx, ty), abs(dx) + abs(dy), dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    return [int(cand[0][2]), int(cand[0][3])]