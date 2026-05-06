def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))
    if not res:
        cx, cy = w // 2, h // 2
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        return [dx, dy]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    resset = set(res)

    # Immediate capture
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in resset:
            return [dx, dy]

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate move by best resource "swing" advantage over opponent
        best_adv = None
        best_selfd = None
        for rx, ry in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = sd - 1.1 * od  # prefer targets we can reach much earlier
            if best_adv is None or adv < best_adv or (adv == best_adv and sd < best_selfd):
                best_adv = adv
                best_selfd = sd
        # Convert to maximization score; lower adv is better
        score = -best_adv
        # Tie-breakers: prefer moving closer to nearest resource and away from obstacles not needed (already valid)
        if best is None or score > best or (score == best and best_selfd < best_selfd2):
            best = score
            best_selfd2 = best_selfd
            best_move = [dx, dy]

    return best_move