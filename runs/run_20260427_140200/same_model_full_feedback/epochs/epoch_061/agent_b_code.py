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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_dx, best_dy = 0, 0
    best_score = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = 0
            min_self = 10**9
            min_opp = 10**9
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                if sd < min_self: min_self = sd
                if od < min_opp: min_opp = od
                # Prefer resources we can reach at least as fast; punish those opponent likely takes first.
                score += (od - sd) * 10
                # Strongly favor immediate/near captures
                if sd == 0:
                    score += 10**6
                elif sd == 1:
                    score += 2000
            # Also incorporate global tendency to get ahead in "closest" race
            score += (min_opp - min_self) * 50
            # Mild tie-break: prefer moves that increase distance from opponent (avoid collision/contested)
            score += cheb(nx, ny, ox, oy) * 2
            if score > best_score:
                best_score = score
                best_dx, best_dy = dx, dy
    else:
        # No resources: move to maximize distance from opponent.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best_score:
                best_score = d
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]