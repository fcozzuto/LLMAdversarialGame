def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role) or ("prey" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role) or ("prey" in opp_role)
    act_as_evader = self_ev or (not opp_ev and self_role == "")

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da > db else db

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    best = None
    best_score = None
    # Deterministic tie-breaking: prefer lexicographically smaller (dx,dy)
    for dx, dy in sorted(dirs):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_now = cheb(nx, ny, ox, oy)
        corner_bias = max(cheb(nx, ny, cx, cy) for cx, cy in corners)
        # Evader: maximize distance; also move toward farthest corner (to prevent corner-locked cycles).
        # Pursuer: minimize distance; also avoid pushing into "dead" squares near obstacles by slightly rewarding open area.
        if act_as_evader:
            # Risk reduction: penalize moves that reduce distance sharply.
            score = (d_now * 1000) + (corner_bias * 3) - (cheb(sx, sy, ox, oy) - d_now) * 50
        else:
            # Open-area heuristic
            open_cnt = 0
            for adx, ady in dirs:
                tx, ty = nx + adx, ny + ady
                if ok(tx, ty):
                    open_cnt += 1
            score = (-d_now * 1000) + (open_cnt * 2)
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]