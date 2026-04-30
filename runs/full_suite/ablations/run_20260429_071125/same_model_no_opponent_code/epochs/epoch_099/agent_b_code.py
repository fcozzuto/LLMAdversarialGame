def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if resources:
        best = None
        bestd = 10**9
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if d < bestd:
                bestd = d
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = ox, oy

    bestm = (0, 0)
    bestscore = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer reducing distance; slightly prefer moving toward opponent when no resources
        d = cheb(nx, ny, tx, ty)
        score = d
        if not resources:
            score = d - 0.01 * cheb(nx, ny, ox, oy)
        if score < bestscore:
            bestscore = score
            bestm = (dx, dy)

    dx, dy = bestm
    if valid(sx + dx, sy + dy):
        return [dx, dy]
    return [0, 0]