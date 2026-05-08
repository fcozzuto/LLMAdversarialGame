def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)] + [(0, 0)]

    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def best_target_score(px, py):
        best = None
        for rx, ry in resources:
            self_d = md(px, py, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            # race win first; then reduce distance; then slight preference for high opp pressure
            key = (opp_d - self_d, -self_d, opp_d)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[0]

    best_move = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        k = best_target_score(nx, ny)
        # prefer moves that keep lead; break ties by aiming to be closer than opponent
        win_bias = (k[0] > 0) - (k[0] < 0)
        move_key = (k, win_bias, -md(nx, ny, ox, oy), nx, ny, dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]