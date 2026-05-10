def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < W and 0 <= by < H:
                blocked.add((bx, by))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_set = set((int(x), int(y)) for x, y in self_terr if x is not None and y is not None)
    opp_set = set((int(x), int(y)) for x, y in opp_terr if x is not None and y is not None)

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(x), int(y)) for x, y in unclaimed if x is not None and y is not None)

    cx, cy = (W - 1) // 2, (H - 1) // 2
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in blocked

    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0
        if (nx, ny) in opp_set:
            score += 20
        elif (nx, ny) in un_set:
            score += 6
        elif (nx, ny) in self_set:
            score += 1
        else:
            score += 0

        dist_now = abs(sx - cx) + abs(sy - cy)
        dist_new = abs(nx - cx) + abs(ny - cy)
        score += (dist_now - dist_new) * 2

        # If we can expand into a promising frontier, prefer it deterministically
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]