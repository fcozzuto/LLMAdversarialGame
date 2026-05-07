def choose_move(observation):
    def pos(key, d=(0, 0)):
        p = observation.get(key, d)
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        return d[0], d[1]

    sx, sy = pos("self_position")
    ox, oy = pos("opponent_position")
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    ti = int(observation.get("turn_index", 0) or 0)
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Prefer targets where we have a timing edge; tie-break toward closer and deterministic parity.
        advantage = do - ds
        key = (advantage, -ds, ((rx + ry + ti) & 1))
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    steps = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles

    # If resource is adjacent (including diagonal), go directly to it if possible.
    adj = (tx - sx, ty - sy)
    if adj[0] in (-1, 0, 1) and adj[1] in (-1, 0, 1):
        nx, ny = tx, ty
        if valid(nx, ny):
            return [adj[0], adj[1]]

    target_dir = (0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1))
    # Choose move that most improves our distance, while avoiding stepping into obstacles.
    best_move = [0, 0]
    best_score = None
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = manh(nx, ny, tx, ty)
        od = manh(nx, ny, tx, ty) - manh(ox, oy, tx, ty)
        # Strongly prefer moving toward target_dir; then minimize our distance.
        toward = 1 if (dx, dy) == target_dir else 0
        sc = (toward, -ns, -abs(nx - ox) - abs(ny - oy), -((dx * 3 + dy * 5 + ti) & 7))
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]