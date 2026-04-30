def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Prioritize resources where we have an advantage; break ties by smaller my distance.
            key = (-(opd - myd), myd, cheb(sx, sy, rx, ry), rx, ry)
            # We want minimal key where first component is negative advantage (so better advantage -> more negative opd-myd)
            if best is None or key < best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        # No resources: drift toward center to avoid corners dead-ends.
        tx, ty = w // 2, h // 2

    my_best = None
    my_best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Score: primarily reduce my distance; secondarily increase opponent distance to that target.
        # Also lightly prefer moves that increase separation from opponent when not making progress.
        prog = man(nx, ny, tx, ty) - man(sx, sy, tx, ty)
        sep = man(nx, ny, ox, oy) - man(sx, sy, ox, oy)
        score = (myd, -opd, prog, -sep)
        if my_best_score is None or score < my_best_score:
            my_best_score = score
            my_best = (dx, dy)

    if my_best is None:
        return [0, 0]
    return [int(my_best[0]), int(my_best[1])]