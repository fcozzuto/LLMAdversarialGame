def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs.add((o[0], o[1]))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res.append((r[0], r[1]))
    if not res:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for rx, ry in res:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        key = (-(od - sd), sd, rx + ry)  # minimize: negative advantage first => prefer larger (od-sd)
        # Equivalent: prefer (od - sd) max; tie: smaller sd; then smaller rx+ry
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key
    tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        d_self = manh(nx, ny, tx, ty)
        d_opp = manh(ox, oy, tx, ty)
        # Prefer getting closer, while keeping/improving relative advantage
        # Larger (d_opp - d_self) is better => minimize negative of it.
        adv = d_opp - d_self
        key = (-adv, d_self, abs(dx) + abs(dy), nx + ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]