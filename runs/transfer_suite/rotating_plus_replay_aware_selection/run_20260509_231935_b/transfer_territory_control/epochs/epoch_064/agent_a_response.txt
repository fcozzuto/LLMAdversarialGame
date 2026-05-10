def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inside(x, y) and (x, y) not in obs
    def man(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx + dy

    candidates = observation.get("unclaimed_cells") or []
    if not candidates:
        ot = observation.get("opponent_territory") or []
        candidates = ot if ot else [(ox, oy)]

    best_target = None
    best_val = None
    for p in candidates:
        if not (isinstance(p, (list, tuple)) and len(p) == 2): 
            continue
        tx, ty = int(p[0]), int(p[1])
        if not legal(tx, ty): 
            continue
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # Prefer targets we can reach sooner; slightly prefer center/edges.
        edge = 1 if (tx == 0 or ty == 0 or tx == w - 1 or ty == h - 1) else 0
        val = (do - ds) + 0.1 * edge
        if best_val is None or val > best_val:
            best_val = val; best_target = (tx, ty)

    if best_target is None:
        best_target = (ox, oy)

    tx, ty = best_target
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # Prefer moves that reduce distance to the chosen target and increase our lead.
        lead = do - ds
        edge = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        # Small bias to avoid moving away from any currently unclaimed cell.
        bias = 0
        for i in range(0, min(3, len(observation.get("unclaimed_cells") or []))):
            q = observation["unclaimed_cells"][i]
            if isinstance(q, (list, tuple)) and len(q) == 2 and legal(int(q[0]), int(q[1])):
                bias -= 0.01 * man(nx, ny, int(q[0]), int(q[1]))
        score = lead + 0.2 * edge - 0.01 * ds + bias
        if best_score is None or score > best_score:
            best_score = score; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]