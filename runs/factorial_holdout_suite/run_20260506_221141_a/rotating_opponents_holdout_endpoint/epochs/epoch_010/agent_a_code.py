def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources_raw = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []

    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        best_val = -10**18
        tx = ty = resources[0][0]
        for r in resources:
            rx, ry = r
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            val = (do - ds) * 100 - ds  # prioritize resources we are likely to secure
            if val > best_val or (val == best_val and (rx, ry) < (tx, ty)):
                best_val = val
                tx, ty = rx, ry

        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            cur = abs(tx - sx) + abs(ty - sy)
            nxt = abs(tx - nx) + abs(ty - ny)
            opp_next = abs(tx - ox) + abs(ty - oy)  # keep simple/deterministic
            # prefer larger reduction; tie-break deterministically
            score = (cur - nxt) * 1000 - nxt - opp_next * 0 + (-(dx * dx + dy * dy))
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources visible: move toward the farthest corner from opponent.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), -c[0], -c[1]))
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = -(abs(cx - nx) + abs(cy - ny))
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]