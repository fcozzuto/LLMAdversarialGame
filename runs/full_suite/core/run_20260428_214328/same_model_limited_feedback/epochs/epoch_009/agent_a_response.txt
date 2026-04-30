def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(a, b): return 0 <= a < W and 0 <= b < H
    def dist(a, b, c, d): return max(abs(a-c), abs(b-d))  # Chebyshev

    # Pick target resource: maximize advantage (opponent further than us) and proximity.
    best_t = None
    best_s = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md = dist(x, y, rx, ry)
        od = dist(ox, oy, rx, ry)
        s = (od - md) * 10 - md  # large weight on relative advantage, small on distance
        if s > best_s:
            best_s = s
            best_t = (rx, ry)

    if best_t is None:
        # No resources: try to move away from opponent while avoiding obstacles.
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            od = dist(nx, ny, ox, oy)
            obs_pen = sum(1 for ex, ey in obstacles if max(abs(nx-ex), abs(ny-ey)) == 1)
            s = od * 3 - obs_pen
            if s > best[2]:
                best = (dx, dy, s)
        dx, dy, _ = best
        return [dx, dy]

    tx, ty = best_t

    # Evaluate candidate moves.
    best = (-10, -10, -10**9)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = dist(nx, ny, tx, ty)
        oppd = dist(nx, ny, ox, oy)

        # Prefer reaching target faster, also keep away from opponent and from obstacles.
        obs_adj = 0
        for ex, ey in obstacles:
            if max(abs(nx-ex), abs(ny-ey)) == 1:
                obs_adj += 1
        s = (-myd) * 20 + (oppd) * 2 - obs_adj * 3

        if s > best[2] or (s == best[2] and (dx, dy) < (best[0], best[1])):
            best = (dx, dy, s)

    dx, dy, _ = best
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]