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

    best_r = None
    best_adv = -10**9
    best_ds = 10**9
    for x, y in resources:
        ds = dist_cheb(sx, sy, x, y)
        do = dist_cheb(ox, oy, x, y)
        adv = do - ds  # our advantage if positive
        if adv > best_adv or (adv == best_adv and ds < best_ds) or (adv == best_adv and ds == best_ds and (x + y) < (best_r[0] + best_r[1] if best_r else 10**9)):
            best_adv = adv
            best_ds = ds
            best_r = (x, y)

    tx, ty = best_r

    def cell_adv(x, y):
        ds = dist_cheb(x, y, tx, ty)
        do = dist_cheb(ox, oy, tx, ty)
        return do - ds

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        val = cell_adv(nx, ny)
        # Small tie-break: closer to target, then towards same general direction
        dcur = dist_cheb(nx, ny, tx, ty)
        if val > best_val or (val == best_val and dcur < dist_cheb(sx, sy, tx, ty)) or (val == best_val and dcur == dist_cheb(sx, sy, tx, ty) and (dx, dy) == (0, 0)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]