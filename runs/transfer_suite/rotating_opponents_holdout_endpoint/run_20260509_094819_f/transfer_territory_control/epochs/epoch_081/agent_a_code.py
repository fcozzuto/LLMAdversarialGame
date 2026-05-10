def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is None:
            continue
        try:
            x, y = p
        except Exception:
            continue
        if x is None or y is None:
            continue
        obstacles.add((int(x), int(y)))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    closest_opp = 1_000_000
    if opp_t:
        for ax, ay in opp_t:
            d = mdist(sx, sy, ax, ay)
            if d < closest_opp:
                closest_opp = d

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 100
        elif (nx, ny) in self_t:
            score += 10
        elif (nx, ny) in unclaimed:
            score += 30
        else:
            score += 0

        d_opp = mdist(nx, ny, ox, oy)
        score += -d_opp

        if opp_t:
            d_to_opp_t = 1_000_000
            for ax, ay in opp_t:
                dd = mdist(nx, ny, ax, ay)
                if dd < d_to_opp_t:
                    d_to_opp_t = dd
            score += -5 * d_to_opp_t

        if observation.get("resources") and isinstance(observation["resources"], (list, tuple)):
            for rx, ry in observation["resources"]:
                if rx is None or ry is None:
                    continue
                score += -2 * mdist(nx, ny, int(rx), int(ry))

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best