def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        pts = observation.get(key) or []
        out = set()
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                out.add((x, y))
        return out

    obstacles = to_set("obstacles") | to_set("obstacle_cells") | to_set("blocked_cells")
    unclaimed = to_set("unclaimed_cells") | to_set("unclaimed") | to_set("neutral_cells")
    self_terr = to_set("self_territory") | to_set("territory")
    opp_terr = to_set("opponent_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [d for d in dirs if d != (0, 0)]

    def adj_to_self(x, y):
        for dx, dy in neigh:
            if (x + dx, y + dy) in self_terr:
                return True
        return False

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target = None
    best = None
    if unclaimed:
        for x, y in unclaimed:
            if not inb(x, y) or (x, y) in obstacles:
                continue
            if self_terr and not adj_to_self(x, y):
                continue
            sc = manh(sx, sy, x, y)
            sc += 0.001 * (abs(x - (w - 1) / 2) + abs(y - (h - 1) / 2))
            if best is None or sc < best:
                best, target = sc, (x, y)

    if target is None:
        target = (ox, oy)

    best_move = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = manh(nx, ny, target[0], target[1])
        if (nx, ny) in opp_terr:
            score += 1000
        if self_terr and (nx, ny) not in self_terr:
            if unclaimed and (nx, ny) not in unclaimed:
                score += 5
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]