def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    def adj_obs_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    p += 1
        return p

    # score: prefer resources where we can close the gap vs opponent; also prefer keeping away from obstacles
    def best_target_score(px, py):
        best = None
        for rx, ry in resources:
            sd = manh(px, py, rx, ry)
            od = manh(ox, oy, rx, ry)
            # emphasize reducing opponent advantage; smaller sd better; avoid very hard targets
            key = (od - sd, -(sd), od, -abs(rx - px) - abs(ry - py), rx, ry)
            if best is None or key > best:
                best = key
        return best[0] if best is not None else -10**9, best

    # If opponent is about to grab a resource next, bias to other targets / positions
    opp_next = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = ox + dx, oy + dy
            if inb(nx, ny):
                opp_next.append((nx, ny))
    # Build set of resources that opponent could reach next (distance 1 with diagonal)
    opp_reach = set()
    for rx, ry in resources:
        if any(abs(nx - rx) <= 1 and abs(ny - ry) <= 1 for nx, ny in opp_next):
            opp_reach.add((rx, ry))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inb(sx + dx, sy + dy)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue

        score_gap, key = best_target_score(nx, ny)
        rx, ry = key[4], key[5] if key is not None else (sx, sy)

        # One-step threat: if opponent can also reach that resource immediately, penalize a lot
        threatened = 1 if (rx, ry) in opp_reach and manh(ox, oy, rx, ry) <= 2 else 0

        # discourage stepping into obstacle-adjacent and getting too close to opponent
        opp_close = 1 if max(abs(nx - ox), abs(ny - oy)) <= 1 else 0
        val = (
            4 * score_gap
            - 1.5 * adj_obs_pen(nx, ny)
            - 2.0 * threatened
            - 0.8 * opp_close
            + 0.05 * (manh(nx, ny, rx, ry) * -1)
        )

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]