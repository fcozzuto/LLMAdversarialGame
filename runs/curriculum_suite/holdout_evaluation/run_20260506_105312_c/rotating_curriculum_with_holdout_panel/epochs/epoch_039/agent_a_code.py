def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def block(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    myd = []
    oppd = []
    for rx, ry in resources:
        myd.append((cheb(sx, sy, rx, ry), rx, ry))
        oppd.append((cheb(ox, oy, rx, ry), rx, ry))
    myd.sort()
    oppd.sort()
    my_target = myd[0][1], myd[0][2]
    opp_target = oppd[0][1], oppd[0][2]

    def choose_target():
        for d, rx, ry in myd:
            if cheb(ox, oy, rx, ry) >= d:
                return (rx, ry)
        return my_target

    tx, ty = choose_target()

    best = None
    best_score = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or block(nx, ny):
                continue
            score = 0
            score -= 3 * cheb(nx, ny, tx, ty)
            if (nx, ny) == (tx, ty):
                score += 1000
            od = cheb(ox, oy, tx, ty)
            score -= 1.5 * od
            # If opponent is racing my target, keep distance from them a bit
            score += 0.8 * cheb(nx, ny, ox, oy)
            if (nx, ny) == (ox, oy):
                score -= 500
            if best is None or score > best_score:
                best_score = score
                best = [dx, dy]
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]