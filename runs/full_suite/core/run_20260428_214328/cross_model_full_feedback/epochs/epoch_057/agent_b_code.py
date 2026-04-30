def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def dist_cheb(a, b):
        dx = abs(a[0]-b[0]); dy = abs(a[1]-b[1])
        return dx if dx>dy else dy

    # If there is a resource, head toward closest resource while staying mindful of opponent
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d = dist_cheb((sx, sy), (rx, ry))
            od = dist_cheb((ox, oy), (rx, ry))
            score = (d, -od)
            if best_score is None or score < best_score:
                best = (rx, ry)
                best_score = score
        if best is not None:
            tx, ty = best
            dx = tx - sx
            dy = ty - sy
            dx = -1 if dx < 0 else (1 if dx > 0 else 0)
            dy = -1 if dy < 0 else (1 if dy > 0 else 0)
            return [dx, dy]

    # Otherwise, move toward center to balance and then adjust away from opponent if possible
    tx, ty = w // 2, h // 2
    dx = tx - sx; dx = -1 if dx < 0 else (1 if dx > 0 else 0)
    dy = ty - sy; dy = -1 if dy < 0 else (1 if dy > 0 else 0)

    # If center move blocked, try to sidestep away from opponent
    if (sx + dx, sy + dy) in obst or not inside(sx + dx, sy + dy):
        # try to pick a safe adjacent move avoiding obstacle and staying near center
        cand = []
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                nx, ny = sx + ax, sy + ay
                if not inside(nx, ny): continue
                if (nx, ny) in obst: continue
                cdx = nx - sx
                cdy = ny - sy
                cand.append((cdx, cdy))
        if cand:
            # choose the candidate with minimal Chebyshev distance to center and furthest from opponent
            best_c = None
            best_score = None
            for cdx, cdy in cand:
                nx, ny = sx + cdx, sy + cdy
                dist_center = max(abs(nx - tx), abs(ny - ty))
                dist_opp = dist_cheb((nx, ny), (ox, oy))
                score = (dist_center, -dist_opp)
                if best_score is None or score < best_score:
                    best_score = score
                    best_c = (cdx, cdy)
            if best_c is not None:
                return [int(best_c[0]), int(best_c[1])]

    return [dx, dy]