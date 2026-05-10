def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    cand_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                cand_res.append((x, y))
    if not cand_res:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Choose a target that we can likely reach first; otherwise deny the opponent's nearest good picks.
    # Deterministic scoring: higher is better.
    best_t = None
    best_sc = None
    for rx, ry in cand_res:
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        # margin>0 means we arrive no later than opponent (using Chebyshev step cost)
        margin = oppd - myd
        # Prefer nearer and also slightly toward center to reduce corner traps.
        center_pen = (abs(rx - cx) + abs(ry - cy)) * 0.05
        sc = margin * 100.0 - myd * 1.3 - center_pen
        # If we can't beat them, still consider but strongly prefer "least worse" denials.
        if best_sc is None or sc > best_sc or (sc == best_sc and (rx, ry) < best_t):
            best_sc = sc
            best_t = (rx, ry)

    tx, ty = best_t

    # Move one step toward target (diagonal allowed), while not stepping into obstacles.
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))
    deltas.sort()  # deterministic lexicographic

    best_m = (0, 0)
    best_v = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Avoid stepping onto an opponent-favored resource if we can do better.
        mydist = cheb(nx, ny, tx, ty)
        oppdist = cheb(ox, oy, tx, ty)
        # If we can improve our arrival relative to them, prioritize; else keep greedy toward target.
        v = -mydist * 2.0 + (oppdist - mydist) * 0.5
        if best_v is None or v > best_v or (v == best_v and (dx, dy) < best_m):
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]