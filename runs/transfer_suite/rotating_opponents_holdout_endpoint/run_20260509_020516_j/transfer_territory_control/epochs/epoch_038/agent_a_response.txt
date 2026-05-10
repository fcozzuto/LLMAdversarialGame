def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    targets = list(unclaimed)
    if not targets:
        targets = list((observation.get("unclaimed_cells") or [])[:])

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    nbrs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not targets:
        # fallback: move toward center, but dodge obstacles and avoid opponent if adjacent
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        best = (10**9, 0, 0, 0)
        for dx, dy in nbrs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
                continue
            d_center = abs(nx - cx) + abs(ny - cy)
            d_opp = man((nx, ny), (ox, oy))
            score = d_center + (0 if d_opp > 1 else 3)
            key = (score, -d_opp, dx, dy)
            if key < best:
                best = (score, dx, dy, 0)
        return [int(best[1]), int(best[2])]

    # choose nearest target with tie-break to prefer stealing moves
    target = min(targets, key=lambda t: (man((sx, sy), t), t[0], t[1]))
    tx, ty = target

    best_key = None
    best_move = (0, 0)
    for dx, dy in nbrs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue

        d_t = man((nx, ny), (tx, ty))
        d_o = man((nx, ny), (ox, oy))
        cell_bonus = 0
        if (nx, ny) in opp_t:
            cell_bonus += 120  # flipping into opponent territory
        elif (nx, ny) in unclaimed:
            cell_bonus += 40   # immediate expansion
        elif (nx, ny) in self_t:
            cell_bonus += 0

        # If opponent is very close, prioritize moves that increase distance to reduce risk
        risk = 0 if d_o > 2 else (5 - d_o) * 10

        # Lower is better; include deterministic tie-break
        key = (d_t - cell_bonus + risk, -d_o, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]