def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def nearest_dist(x, y, pts):
        if not pts:
            return 10**9
        md = 10**9
        for rx, ry in pts:
            d = man(x, y, rx, ry)
            if d < md:
                md = d
        return md

    def count_near(x, y, pts, thr=2):
        c = 0
        for rx, ry in pts:
            if man(x, y, rx, ry) <= thr:
                c += 1
        return c

    best_score = None
    best_move = [0, 0]

    any_res = bool(resources)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        if any_res:
            dres = nearest_dist(nx, ny, resources)
            bonus = count_near(nx, ny, resources, 2)
            # Approx deny: opponent's best immediate move to nearest resource
            opp_best_dres = 10**9
            for odx, ody in deltas:
                tx, ty = ox + odx, oy + ody
                if blocked(tx, ty):
                    continue
                dtmp = nearest_dist(tx, ty, resources)
                if dtmp < opp_best_dres:
                    opp_best_dres = dtmp
            dopp = man(nx, ny, ox, oy)
            score = (-dres) + 0.8 * bonus + 0.15 * dopp - 0.6 * opp_best_dres
        else:
            # No resources left: drift to center while avoiding invalid moves
            cx, cy = (w - 1) / 2, (h - 1) / 2
            score = -abs(nx - cx) - abs(ny - cy) - 0.05 * man(nx, ny, ox, oy)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move