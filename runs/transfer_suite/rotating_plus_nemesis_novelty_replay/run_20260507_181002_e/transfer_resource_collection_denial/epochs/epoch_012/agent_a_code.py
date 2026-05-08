def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict) and "position" in p:
            q = p["position"]
            if isinstance(q, (list, tuple)) and len(q) == 2:
                obs_set.add((int(q[0]), int(q[1])))

    res_list = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res_list.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", r.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                res_list.append((int(q[0]), int(q[1])))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            moves.append((dx, dy))
    if not moves:
        return [0, 0]

    opp_close = man(sx, sy, ox, oy) <= 2
    center = (w - 1) / 2.0, (h - 1) / 2.0

    best = None  # (score, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_res = 10**9
        for rx, ry in res_list:
            d = man(nx, ny, rx, ry)
            if d < d_res:
                d_res = d
        if res_list:
            # Prefer getting closer to nearest resource; slightly prefer attacking when resources exist.
            score = (-d_res, -man(nx, ny, ox, oy))
        else:
            # No visible resources: go toward center; if close to opponent, bias away.
            d_cent = abs(nx - center[0]) + abs(ny - center[1])
            score = (-d_cent, man(nx, ny, ox, oy) if opp_close else -man(nx, ny, ox, oy))
        cand = (score, dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[1]), int(best[2])]