def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = w // 2, h // 2
    if not resources:
        tx, ty = cx, cy
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0] or (d == best[0] and (nx, ny) < (best[1], best[2])):
                best = (d, nx, ny)
        return [best[1] - sx, best[2] - sy]

    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        key = (-adv, sd, rx, ry)  # minimize negative advantage => maximize adv; tie by closer then lexicographic
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    od = cheb(ox, oy, rx, ry)
    best_move = (-(10**9), 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        nsd = cheb(nx, ny, rx, ry)
        adv_next = od - nsd
        dmid = cheb(nx, ny, cx, cy)
        score1 = adv_next
        score2 = nsd
        # Prefer higher advantage; then smaller distance to target; then closer to center; then lexicographic move
        cand = (score1, -score2, -dmid, nx, ny)
        if cand > best_move:
            best_move = cand

    nx, ny = best_move[3], best_move[4]
    return [nx - sx, ny - sy]