def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < gw and 0 <= y < gh:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    best = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd
        score = margin * 1000 - sd
        if margin <= 0:
            score -= od
        if score > best_score:
            best_score = score
            best = (rx, ry)

    rx, ry = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_d = 10**9
    best_margin = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obs:
            continue
        d = cheb(nx, ny, rx, ry)
        md = cheb(ox, oy, rx, ry) - d
        if d < best_d or (d == best_d and md > best_margin):
            best_d = d
            best_margin = md
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]