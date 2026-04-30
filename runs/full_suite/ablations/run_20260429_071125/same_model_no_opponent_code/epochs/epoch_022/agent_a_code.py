def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    x, y, ox, oy = int(x), int(y), int(ox), int(oy)
    occ = set()
    for p in obstacles:
        if p and len(p) >= 2:
            occ.add((int(p[0]), int(p[1])))

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    res = []
    for p in resources:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if inb(rx, ry) and (rx, ry) not in occ:
                res.append((rx, ry))
    res.sort()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if res:
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            # Value = best (our closeness to a resource, while pushing opponent away from it)
            val = -10**18
            for rx, ry in res:
                d1 = manh(nx, ny, rx, ry)
                d2 = manh(ox, oy, rx, ry)
                cur = -d1 + 0.5 * d2
                if cur > val:
                    val = cur
            # Tie-break: prefer staying closer to any resource
            if val > best_val or (val == best_val and (manh(nx, ny, res[0][0], res[0][1]) < manh(x, y, res[0][0], res[0][1]))):
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: move to block/press opponent (deterministic greedy chase)
    tx, ty = ox, oy
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        d = manh(nx, ny, tx, ty)
        val = -d
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    # Fallback: stay if all moves blocked, otherwise first valid
    if (x, y) not in occ and inb(x, y):
        return [0, 0]
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) not in occ:
            return [dx, dy]
    return [0, 0]