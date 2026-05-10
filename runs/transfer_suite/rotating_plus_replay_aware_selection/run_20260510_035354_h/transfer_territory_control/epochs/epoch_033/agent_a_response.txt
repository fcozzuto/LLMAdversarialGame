def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for x, y in obstacles:
        if inb(x, y):
            obs.add((x, y))

    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    my_set = set((x, y) for x, y in my_t if inb(x, y))
    op_set = set((x, y) for x, y in op_t if inb(x, y))
    un_set = set((x, y) for x, y in unclaimed if inb(x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    def dist2(p, q):
        dx = p[0] - q[0]
        dy = p[1] - q[1]
        return dx * dx + dy * dy

    # Target set: unclaimed cells that are adjacent to opponent territory (best stealing chances)
    targets = []
    if un_set:
        for ux, uy in un_set:
            for nx, ny in neighbors8(ux, uy):
                if (nx, ny) in op_set:
                    targets.append((ux, uy))
                    break

    if not targets:
        targets = list(un_set)
    if not targets:
        targets = list(op_set)
    if not targets:
        return [0, 0]

    # Rank move outcomes by immediate heuristic
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        p = (nx, ny)

        score = 0
        if p in un_set:
            score += 40
            # extra for entering unclaimed near opponent (maximize flipping tempo)
            for nnx, nny in neighbors8(nx, ny):
                if (nnx, nny) in op_set:
                    score += 12
                    break
        elif p in op_set:
            score += 18  # allow flipping on entry
        elif p in my_set:
            score += 4   # maintain control

        # Prefer closer to chosen targets (take nearest among a small deterministic subset)
        targets_sorted = sorted(targets, key=lambda t: dist2(p, t))
        k = 4 if len(targets_sorted) >= 4 else len(targets_sorted)
        if k > 0:
            score += max(-dist2(p, targets_sorted[i]) for i in range(k)) / 10.0

        # Slightly penalize moves that directly approach obstacles (avoid obstacle-sticking)
        adj_obs = 0
        for nnx, nny in neighbors8(nx, ny):
            if (nnx, nny) in obs:
                adj_obs += 1
        score -= adj_obs * 2

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]