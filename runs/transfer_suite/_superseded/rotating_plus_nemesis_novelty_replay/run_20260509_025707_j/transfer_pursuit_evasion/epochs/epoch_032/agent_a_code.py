def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_for_pos(nx, ny):
        d = cheb(nx, ny, ox, oy)
        # Constraint term: reduce opponent mobility by approaching the area around them.
        mob = 0
        for dx, dy in deltas:
            tx, ty = ox + dx, oy + dy
            if 0 <= tx < w and 0 <= ty < h:
                if (tx, ty) in obstacles:
                    mob += 1
                else:
                    mob -= 0  # keep deterministic structure
        # Obstacle proximity penalty (prevents "wall-run" trapping mistakes).
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    prox += 1
        # Corner pressure: prefer moving toward the farthest corner when evading, else toward the nearest.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # For determinism, compute min/max over fixed corners.
        dist_to_corners = [cheb(nx, ny, cx, cy) for (cx, cy) in corners]
        minc = min(dist_to_corners)
        maxc = max(dist_to_corners)

        if is_evader:
            # Evade: maximize distance; also try to move toward corners; avoid obstacle vicinity.
            return 10 * d + 0.6 * maxc - 0.8 * prox
        else:
            # Pursue: minimize distance; also try to reduce opponent "mobility" neighborhood via positioning
            # (mob is computed as number of blocked neighbor cells), and avoid obstacles nearby.
            return -10 * d + 0.6 * mob - 0.8 * prox + 0.05 * (-minc)

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = score_for_pos(nx, ny)
        if best is None or sc > best:
            best = sc
            best_move = [dx, dy]
    return best_move