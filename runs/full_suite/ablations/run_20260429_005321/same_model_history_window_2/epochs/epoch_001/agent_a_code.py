def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h

    if not resources:
        # No resources visible: move to center to reduce symmetry with deterministic choice
        cx, cy = w // 2, h // 2
        best_d = [0, 0]
        best = -10**9
        for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - cx) + abs(ny - cy)
            val = -d
            if val > best:
                best = val
                best_d = [dx, dy]
        return best_d

    # Choose target deterministically: nearest by BFS-like metric using Manhattan, tie by coordinate
    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    tx, ty = min(resources, key=lambda p: (dist(x, y, p[0], p[1]), p[0], p[1]))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Tie-break order deterministic
    deltas.sort(key=lambda d: (d[0], d[1]))

    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary objective: reduce distance to target
        d_t = dist(nx, ny, tx, ty)

        # Bonus if stepping onto a resource
        on_resource = (nx, ny) in set(tuple(p) for p in resources)
        bonus_resource = -120 if on_resource else 0

        # Secondary: avoid walking directly toward opponent when close, but still keep pressure
        d_o = dist(nx, ny, ox, oy)
        # If opponent is very close, slightly prefer increasing distance
        opp_term = 0
        if d_o <= 3:
            opp_term = d_o * 6  # prefer larger d_o

        # Mild preference to not stay still unless best
        stay_pen = -2 if (dx == 0 and dy == 0) else 0

        val = (-d_t) + bonus_resource + opp_term + stay_pen

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move