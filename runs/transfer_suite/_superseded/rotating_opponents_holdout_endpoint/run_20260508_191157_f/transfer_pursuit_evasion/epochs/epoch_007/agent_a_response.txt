def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)
    role = observation.get("self_role", "pursuer")
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def free_neighbors(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                cnt += 1
        return cnt

    def dir_sign(t, s):
        return 0 if t == s else (1 if t > s else -1)

    if role == "pursuer":
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs:
                continue
            d = md(nx, ny, ox, oy)
            neigh = free_neighbors(nx, ny)
            # Tie-break: prefer moves that keep mobility and reduce distance aggressively
            key = (d, -neigh, nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # Evader: avoid being cornered by using a "safe corner" objective plus distance gain.
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    # Prefer the corner that is farthest but also has relatively free path space around it.
    def corner_score(cx, cy):
        return md(sx, sy, cx, cy) + 0.1 * md(ox, oy, cx, cy) - 0.01 * (w + h) + free_neighbors(cx, cy)
    target = max(corners, key=lambda p: md(p[0], p[1], ox, oy) + 0.25 * corner_score(p[0], p[1]))

    tx, ty = target
    avoid_ox_dirx = -dir_sign(ox, sx)
    avoid_ox_diry = -dir_sign(oy, sy)

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        d = md(nx, ny, ox, oy)
        to_corner = md(nx, ny, tx, ty)
        # Strongly reward increasing distance; softly reward progressing to a "safe" corner.
        # Also discourage moving toward opponent direction (helps against zigzag).
        toward_opponent = (dx == dir_sign(ox, sx) and dy == dir_sign(oy, sy))
        neigh = free_neighbors(nx, ny)
        key = (-d, to_corner, toward_opponent, -(neigh), nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1] if best is not None else [0, 0]