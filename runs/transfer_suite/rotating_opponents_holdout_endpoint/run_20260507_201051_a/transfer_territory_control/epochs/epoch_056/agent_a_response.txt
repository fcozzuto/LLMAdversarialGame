def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    raw_ob = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in raw_ob)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    selfT = set((p[0], p[1]) for p in (observation.get("self_territory") or []))
    oppT = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells") or []))

    # Build opponent frontier cells (empty or our/ unclaimed) adjacent to their territory
    opp_front = []
    for ox, oy in oppT:
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = ox + dx, oy + dy
            if inb(nx, ny) and ((nx, ny) not in oppT):
                opp_front.append((nx, ny))
    opp_front = list(dict.fromkeys(opp_front))

    # If no frontier yet, just head to nearest unclaimed cell
    if not opp_front:
        targets = list(unclaimed)
        if not targets:
            targets = [(w // 2, h // 2)]
        # Choose deterministically by manhattan then coordinate
        tx, ty = min(targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        # Pick best frontier by distance to us
        tx, ty = min(opp_front, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))

    # Evaluate each possible move by one-step gain toward cutting/claiming frontier
    best = (-(10**9), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0
        if (nx, ny) in oppT:
            score += 120  # flipping their cell is strong
        elif (nx, ny) in unclaimed:
            score += 70   # extend into free space
        elif (nx, ny) in selfT:
            score += 10   # keep space; still moveable

        # Distance-based shaping toward frontier
        score += 8 - 2 * (abs(nx - tx) + abs(ny - ty))

        # Obstacle pressure: avoid moving adjacent to obstacles that can trap us
        adj_obs = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            px, py = nx + ax, ny + ay
            if not (0 <= px < w and 0 <= py < h) or (px, py) in obstacles:
                adj_obs += 1
        score -= 3 * adj_obs

        # Tie-break deterministically: prefer smaller dx, then smaller dy, then prefer staying if equal
        tie = (score, -abs(dx), -abs(dy), -int(dx == 0 and dy == 0))
        if score > best[0] or (score == best[0] and tie > (best[0], -abs(best[1]), -abs(best[2]), -int(best[1] == 0 and best[2] == 0))):
            best = (score, dx, dy)

    if best[0] < -10**8:
        return [0, 0]
    return [int(best[1]), int(best[2])]