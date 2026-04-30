def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def xy(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return int(q[0]), int(q[1])
        return None

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        q = xy(p)
        if q is not None:
            obstacles.add(q)
    resources = []
    for p in observation.get("resources", []) or []:
        q = xy(p)
        if q is not None:
            resources.append(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    alive = [r for r in resources if r not in obstacles]
    if not alive:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    # Choose a target resource that opponent is relatively farther from (deterministic blocking/claiming).
    best_r = alive[0]
    best_adv = None
    for r in alive:
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        adv = ds - do  # lower means we're closer; higher means opponent farther
        # Prefer resources where opponent is far away: maximize (do - ds)
        key = do - ds
        if best_adv is None or key > best_adv or (key == best_adv and (r[0], r[1]) < (best_r[0], best_r[1])):
            best_adv = key
            best_r = r

    tx, ty = best_r
    # Move to reduce distance to target; avoid obstacles; if tie, prefer moves that also increase claim advantage.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = dist((nx, ny), (tx, ty))
        cur = dist((ox, oy), (tx, ty))
        score = (-ns) + (cur - ns) * 0.25  # primarily go to target; secondary: deny opponent
        # Tiny deterministic tie-break: closer to center of board, then lexicographic
        center = (w - 1) / 2.0, (h - 1) / 2.0
        cen_d = dist((nx, ny), center)
        score2 = score - cen_d * 1e-6
        if best_score is None or score2 > best_score or (score2 == best_score and (dx, dy) < best_move):
            best_score = score2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]