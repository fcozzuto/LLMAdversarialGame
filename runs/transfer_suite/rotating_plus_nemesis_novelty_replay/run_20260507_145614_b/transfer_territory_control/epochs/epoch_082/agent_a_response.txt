def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    opp_set = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opp_set.add((x, y))
    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 12
        if (nx, ny) in opp_set:
            val += 10  # flipping on entry
        # frontier seeking
        frontier = 0
        for ax, ay in neighbors8(nx, ny):
            if (ax, ay) in unclaimed:
                frontier += 1
        val += 2 * frontier
        # avoid getting too close to opponent unless capturing it
        if (nx, ny) not in opp_set:
            near_opp = 0
            for ax, ay in neighbors8(nx, ny):
                if (ax, ay) in opp_set:
                    near_opp += 1
            val -= 2 * near_opp

        # deterministic tie-break: prefer increasing distance from our start diagonal? keep pressure to center then corner-sweep
        dist_center = abs(nx - cx) + abs(ny - cy)
        edge = (1 if nx in (0, w - 1) else 0) + (1 if ny in (0, h - 1) else 0)
        val += -0.01 * dist_center + 0.001 * edge

        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]