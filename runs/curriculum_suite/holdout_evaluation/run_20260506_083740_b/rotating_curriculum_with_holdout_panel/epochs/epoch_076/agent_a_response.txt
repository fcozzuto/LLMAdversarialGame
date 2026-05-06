def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a target resource that we can reach "relatively" sooner than opponent
    # Tie-break deterministically by absolute closeness.
    best_cells = []
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        advantage = sd - od
        best_cells.append((advantage, sd, rx, ry))
    if not best_cells:
        return [0, 0]

    # minimize advantage, then sd, then lexicographic rx,ry for determinism
    best_cells.sort()
    _, _, tx, ty = best_cells[0]

    # Move one step toward target, but ensure validity; otherwise choose best alternative step.
    # Scoring step by improved relative advantage after the move.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nsd = md(nx, ny, tx, ty)
        nod = md(ox, oy, tx, ty)
        # Prefer decreasing relative advantage and also progress to target.
        score = (nsd - nod, nsd, md(nx, ny, tx, ty), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]