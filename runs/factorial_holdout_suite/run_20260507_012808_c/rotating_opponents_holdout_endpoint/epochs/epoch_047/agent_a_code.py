def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    neigh = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            neigh.append((dx, dy))
    neigh.append((0, 0))

    best_move = (0, 0)
    best_val = None

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_d_now = manh(nx, ny, ox, oy)
        # Evaluate best resource after this move; prioritize stealing by being closer than opponent.
        best_res_val = None
        for rx, ry in resources:
            my_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            steal = opp_d - my_d  # positive if we are closer
            # Prefer immediate steal wins; otherwise get closer to something nearer than opponent.
            # Add small bias to reduce distance to opponent (deny sweep lines indirectly).
            val = steal * 120 - my_d * 3 - my_d_now * 0.1
            if best_res_val is None or val > best_res_val:
                best_res_val = val
        if best_val is None or best_res_val > best_val:
            best_val = best_res_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]