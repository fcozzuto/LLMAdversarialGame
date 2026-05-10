def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    role = (observation.get("self_role") or "").lower()
    evader = ("evad" in role) or ("escape" in role) or ("runner" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_res_dist(x, y):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    best = None
    best_val = None
    # Deterministic tie-breaker: prefer smaller dx, then dy lexicographically
    for dx, dy in sorted(moves, key=lambda t: (t[0], t[1])):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_res = nearest_res_dist(nx, ny)

        # Heuristic:
        # - Evader: maximize distance from opponent; slight preference for moving toward resources (to bait opponent/collisions).
        # - Pursuer: minimize distance from opponent; prefer resources only if it doesn't sacrifice approach.
        if evader:
            val = d_opp * 1000 - d_res
        else:
            val = (-d_opp) * 1000 - d_res * 0.1

        # Prefer staying still if values equal to avoid oscillation
        if best_val is None or val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]