def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def to_xy(p):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            q = p.get("position", p.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                return int(q[0]), int(q[1])
        return None

    obs_set = set()
    for p in obstacles:
        t = to_xy(p)
        if t is not None:
            obs_set.add(t)

    res = []
    for r in resources:
        t = to_xy(r)
        if t is not None:
            res.append(t)
    if not res:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_move():
        best_score = None
        best_move = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                continue
            cur_best = None
            for rx, ry in res:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # Prefer resources we can reach first; strongly contest resources opponent is closer to.
                # Add small bias for absolute progress to reduce dithering.
                val = (od - sd) * 10 - sd
                if cur_best is None or val > cur_best:
                    cur_best = val
            if cur_best is None:
                continue
            # Small deterministic preference to avoid oscillation: favor moves that reduce distance to the
            # currently most contested resource (where od - sd is biggest).
            # (Approximated by maximizing cur_best already; use lexicographic tie-break.)
            if best_score is None or cur_best > best_score or (cur_best == best_score and (dx, dy) < best_move):
                best_score = cur_best
                best_move = (dx, dy)
        return list(best_move)

    mv = best_move()
    if mv[0] not in (-1, 0, 1) or mv[1] not in (-1, 0, 1):
        return [0, 0]
    return mv