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

    # Frontier first: unclaimed adjacent to our territory
    frontier = []
    if self_t:
        for (x, y) in self_t:
            for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) in unclaimed:
                    frontier.append((nx, ny))

    # Second: best unclaimed by proximity to our position
    candidates = frontier if frontier else list(unclaimed)

    # Third fallback: push into opponent territory from a reachable direction
    if not candidates:
        candidates = list(opp_t)

    # Choose a single target deterministically
    def dist(a, b):  # Chebyshev is better for diagonal movement
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    target = None
    best = 10**9
    if candidates:
        for t in candidates:
            d = dist((sx, sy), t)
            # small deterministic tie-breaker to reduce oscillation
            tie = (t[0] * 31 + t[1] * 17)
            score = d * 10000 + tie
            if score < best:
                best = score
                target = t

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue

        # Value: approach target, prefer claiming unclaimed, avoid stepping deep into opponent
        if target is not None:
            approach = dist((nx, ny), target)
        else:
            approach = 0

        if (nx, ny) in unclaimed:
            claim_bonus = -5000
        else:
            claim_bonus = 0

        # Penalize entering opponent territory unless it also advances toward target/opportunity
        if (nx, ny) in opp_t:
            opp_penalty = 2000 + dist((nx, ny), (ox, oy))  # generally riskier
        else:
            opp_penalty = 0

        # Encourage staying mobile: slight penalty for standing still (unless no target)
        still_penalty = 50 if (dx == 0 and dy == 0 and target is not None) else 0

        val = approach * 10 + opp_penalty + still_penalty + claim_bonus
        # deterministic tie-break
        val2 = val * 10 + (dx + 1) * 3 + (dy + 1)
        if val2 < best_val:
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]