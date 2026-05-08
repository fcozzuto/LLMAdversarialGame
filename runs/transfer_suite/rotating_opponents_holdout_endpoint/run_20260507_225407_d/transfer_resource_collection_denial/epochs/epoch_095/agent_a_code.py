def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

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
    # Prefer guaranteed lead; otherwise maximize lead. Tie-break by nearer to us, then deterministically by coordinates.
    for x, y in resources:
        our_t = kingdist(sx, sy, x, y)
        opp_t = kingdist(ox, oy, x, y)
        lead = opp_t - our_t  # positive means we arrive earlier in king metric
        guaranteed = 1 if our_t < opp_t else 0
        # Slight bias away from opponent corner-closeness: favor resources that opp is not already "about to" take.
        urgency = -our_t
        key = (guaranteed, lead, urgency, -x, -y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    # Primary move towards target, then alternatives that keep progress without stepping into obstacles.
    candidates.append((dx, dy))
    candidates.append((dx, 0))
    candidates.append((0, dy))
    candidates.append((dx, -dy))
    candidates.append((-dx, dy))
    candidates.append((0, 0))

    for mdx, mdy in candidates:
        nx, ny = sx + mdx, sy + mdy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [int(mdx), int(mdy)]

    return [0, 0]