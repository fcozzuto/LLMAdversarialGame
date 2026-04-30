def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles_in = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles_in:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if inb(x, y):
            obs.add((x, y))

    resources_in = observation.get("resources", []) or []
    resources = []
    for p in resources_in:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if inb(x, y) and (x, y) not in obs:
            resources.append((x, y))

    if not inb(sx, sy) or not inb(ox, oy):
        return [0, 0]
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist_manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_opp_dist_after_one(px, py, rx, ry):
        best = 10**9
        # Opponent assumed to choose best one-step (greedy) ignoring collision with obstacles (engine will prevent).
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = dist_manh(nx, ny, rx, ry)
            if d < best:
                best = d
        return best if best != 10**9 else dist_manh(px, py, rx, ry)

    # Evaluate our best move by maximizing advantage against the most contested resource.
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nsx, nsy = sx + dx, sy + dy
        if not inb(nsx, nsy) or (nsx, nsy) in obs:
            nsx, nsy = sx, sy  # engine would keep us in place
        our_best = -10**18
        for rx, ry in resources:
            our_d = dist_manh(nsx, nsy, rx, ry)
            opp_d = best_opp_dist_after_one(ox, oy, rx, ry)
            # Advantage: we prefer resources where we can get closer sooner than opponent.
            # Add a mild preference for nearer resources to break ties.
            advantage = (opp_d - our_d) * 1000 - our_d
            if advantage > our_best:
                our_best = advantage
            elif advantage == our_best:
                # Deterministic tie-break by resource position
                if (rx, ry) < (0, 0):  # never true; keep stable behavior
                    pass
        score = our_best
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break by delta order in deltas
            if deltas.index((dx, dy)) < deltas.index(best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]