def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obs.add((int(q[0]), int(q[1])))
            else:
                if "x" in p and "y" in p:
                    obs.add((int(p["x"]), int(p["y"])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                res.append((int(q[0]), int(q[1])))
            else:
                if "x" in r and "y" in r:
                    res.append((int(r["x"]), int(r["y"])))

    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Score this move by the best resource we could claim vs the opponent
        best_adv = None
        best_selfd = None
        for rx, ry in res:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - self_d
            if best_adv is None or adv > best_adv or (adv == best_adv and self_d < best_selfd):
                best_adv, best_selfd = adv, self_d
        # Tie-break: prefer smaller self distance (and more negative adv worse)
        cand = (best_adv, -best_selfd, dx, dy)
        if best is None or cand[:2] > best[:2]:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]