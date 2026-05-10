def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)

    def inside(x, y): 
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in observation.get("self_territory") or [])
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory") or [])
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells") or [])
    if not unclaimed and not opp_terr and not self_terr:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cell_value(x, y):
        if (x, y) in obstacles: 
            return -10**9
        if (x, y) in self_terr:
            return 0
        v = 0
        if (x, y) in opp_terr:
            v += 120  # prioritize flipping opponent territory
        if (x, y) in unclaimed:
            v += 70   # claim unclaimed
        # small bonus for being closer to center (reduce being cornered/edge pressured)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        v += 3.0 * (-(abs(x - cx) + abs(y - cy)))
        return int(v)

    best = (cell_value(sx, sy), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = cell_value(nx, ny)
        if v > best[0] or (v == best[0] and (dx, dy) < (best[1], best[2])):
            best = (v, dx, dy)

    if best[0] <= -10**8:
        return [0, 0]

    # If no adjacent target, greedily approach nearest unclaimed/opp cell along best 1-step direction.
    if best[1] == 0 and best[2] == 0:
        targets = list(unclaimed) if unclaimed else list(opp_terr)
        if targets:
            tx, ty = min(targets, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
            dx = 0 if tx == sx else (1 if tx > sx else -1)
            dy = 0 if ty == sy else (1 if ty > sy else -1)
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]

    return [best[1], best[2]]