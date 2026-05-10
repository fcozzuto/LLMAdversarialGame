def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        x, y = p
        obs.add((int(x), int(y)))

    res = []
    for r in resources:
        x, y = r
        ix, iy = int(x), int(y)
        if 0 <= ix < gw and 0 <= iy < gh and (ix, iy) not in obs:
            res.append((ix, iy))

    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def d8(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Focus on a few nearest resources to keep it short
    res.sort(key=lambda p: d8(sx, sy, p[0], p[1]))
    res = res[:8]

    best_mv = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        sc = 0
        # Prefer getting closer to resources, and closer to ones opponent is not already nearer to
        for rx, ry in res:
            ds = d8(nx, ny, rx, ry)
            do = d8(ox, oy, rx, ry)
            # if we are closer than opponent, strongly prefer this target
            if ds < do:
                sc += (do - ds) * 10
            sc -= ds
        # Slightly prefer staying away from immediate contact risk (deterministic, small penalty)
        sc -= d8(nx, ny, ox, oy) // 2

        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    dx, dy = best_mv
    return [int(dx), int(dy)]