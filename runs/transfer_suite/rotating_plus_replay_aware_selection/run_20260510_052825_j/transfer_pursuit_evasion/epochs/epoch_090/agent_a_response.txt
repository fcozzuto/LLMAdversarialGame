def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    pursuer = not evader

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    obs = list(blocked)

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def min_obs_dist2(nx, ny):
        if not obs:
            return 10**9
        md = 10**9
        for x, y in obs:
            dd = dist2(nx, ny, x, y)
            if dd < md:
                md = dd
        return md

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = None
    best_corner = -10**18
    for cx, cy in corners:
        if (cx, cy) in blocked:
            continue
        sc = dist2(cx, cy, ox, oy)
        if sc > best_corner:
            best_corner = sc
            target = (cx, cy)
    if target is None:
        target = (0, 0)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**30 if pursuer else 10**30

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        md2 = min_obs_dist2(nx, ny)
        wall_term = -1.0 / (md2 + 1.0)  # avoid being near obstacles

        if pursuer:
            corner_push = -0.01 * dist2(nx, ny, target[0], target[1])
            score = (-d) + 0.8 * wall_term + corner_push
            if score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            corner_pull = 0.02 * dist2(nx, ny, target[0], target[1])
            score = d + 0.8 * (-wall_term) + corner_pull
            if score < best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]