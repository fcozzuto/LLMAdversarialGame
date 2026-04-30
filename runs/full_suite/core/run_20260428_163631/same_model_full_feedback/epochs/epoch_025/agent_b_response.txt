def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose target resource: favor those we're closer to; otherwise still pick best attainable.
    best = None
    for rx, ry in resources:
        d_self = dist(sx, sy, rx, ry)
        d_opp = dist(ox, oy, rx, ry)
        lead = d_opp - d_self  # positive means we're closer
        # small tie-break on proximity to reduce wandering
        score = (lead * 1000) - d_self
        if best is None or score > best[0] or (score == best[0] and (rx, ry) < best[1]):
            best = (score, (rx, ry), d_self, d_opp)

    # If no resources visible, head to center deterministically.
    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best[1]

    # Move: minimize distance to target; prefer diagonals/ordering deterministically.
    best_move = None
    for dx, dy, nx, ny in legal:
        d = dist(nx, ny, tx, ty)
        # Avoid stepping into a cell that is "worse" than staying when equally good.
        # Also lightly prefer positions that increase separation from opponent.
        sep = dist(nx, ny, ox, oy)
        # deterministic ordering via dirs index
        idx = dirs.index((dx, dy))
        val = ( -d, sep, -idx )
        if best_move is None or val > best_move[0]:
            best_move = (val, dx, dy)

    return [int(best_move[1]), int(best_move[2])]