def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_adv = None
    best_resource = resources[0]
    intercept_resource = None

    for x, y in resources:
        ds = dist_cheb(sx, sy, x, y)
        do = dist_cheb(ox, oy, x, y)
        adv = (do - ds)  # positive: we're closer
        if best_adv is None or adv > best_adv or (adv == best_adv and ds < dist_cheb(sx, sy, best_resource[0], best_resource[1])):
            best_adv = adv
            best_resource = (x, y)
        if do < ds:  # opponent closer
            if intercept_resource is None or ds < dist_cheb(sx, sy, intercept_resource[0], intercept_resource[1]):
                intercept_resource = (x, y)

    target = best_resource
    if best_adv < 0 and intercept_resource is not None:
        target = intercept_resource  # try to intercept/steal nearer contested items

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ns = dist_cheb(nx, ny, tx, ty)
        no = dist_cheb(ox, oy, tx, ty)
        val = (no - ns) * 100 - ns  # prioritize advantage and getting closer
        if val > best_val or (val == best_val and (dx, dy) == (0, 0) and best_move != (0, 0)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]