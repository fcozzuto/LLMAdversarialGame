def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    if resources:
        candidates = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            best = -10**18
            for rx, ry in resources:
                sd = md(nx, ny, rx, ry)
                od = md(ox, oy, rx, ry)
                val = (od - sd) * 100 - sd
                if sd == 0:
                    val += 10**6
                best = val if val > best else best
            candidates.append((best, dx, dy))
        if candidates:
            candidates.sort(reverse=True)
            return [int(candidates[0][1]), int(candidates[0][2])]

    best_move = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # If no safe resource plan, drift toward opponent deterministically.
        val = -md(nx, ny, ox, oy)
        if val > best_move[0]:
            best_move = (val, dx, dy)
    return [int(best_move[1]), int(best_move[2])]