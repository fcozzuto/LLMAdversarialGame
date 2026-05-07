def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs_set:
                resources.append((rx, ry))

    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [dx, dy]

    def steps(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev (diagonal moves allowed)

    best_score = None
    best_t = resources[0]
    for tx, ty in resources:
        sd = steps(sx, sy, tx, ty)
        od = steps(ox, oy, tx, ty)
        # Prefer resources where we are earlier; penalize when opponent is earlier.
        # Tie-break by closer self distance, then by coordinate sum (deterministic).
        score = (od - sd, -sd, -(tx + ty))
        if best_score is None or score > best_score:
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t
    candidates = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If direct move into obstacle, choose best neighbor towards the target by same heuristic.
    def valid(nx, ny): return inb(nx, ny) and (nx, ny) not in obs_set
    best_m = [0, 0]
    best_m_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = steps(nx, ny, tx, ty)
        no = steps(ox, oy, tx, ty)
        ms = (no - ns, -ns, -(nx + ny))
        if best_m_score is None or ms > best_m_score:
            best_m_score = ms
            best_m = [dx, dy]

    return best_m