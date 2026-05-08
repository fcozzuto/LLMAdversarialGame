def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal or not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    # Prefer resources we can reach first; if none, pick the one where opponent advantage is smallest
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        lead = do - ds  # positive: we are closer
        # Tie-break shaping:
        # - primary: maximize lead
        # - secondary: minimize our distance (finish sooner)
        # - tertiary: bias toward cells farther from opponent corner (reduce sweep impact)
        corner_bias = - (md(rx, ry, 7 - ox, 7 - oy))
        score = (lead, -ds, corner_bias)
        if best is None or score > best[0]:
            best = (score, (rx, ry))

    rx, ry = best[1]

    # Choose deterministic step that reduces distance to target; if equal, prefer moves that keep us away from opponent
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to = md(nx, ny, rx, ry)
        d_opp = md(nx, ny, ox, oy)
        # Avoid stepping onto "overshadowed" targets: if opponent is clearly closer, don't rush straight into it.
        # Instead, slightly prefer moves that increase distance to opponent.
        key = ( -d_to, d_opp, -abs(nx - rx) - abs(ny - ry), dx, dy )
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]