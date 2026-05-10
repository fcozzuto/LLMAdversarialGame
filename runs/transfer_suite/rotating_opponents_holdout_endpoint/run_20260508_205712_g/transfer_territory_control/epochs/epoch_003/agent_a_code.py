def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells", []) or [])]
    self_territory = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_territory = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    self_count = observation.get("self_territory_count", 0)
    opp_count = observation.get("opponent_territory_count", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Build a quick adjacency set for opponent territory to bias counterclaims
    opp_adj = set()
    for (x, y) in opp_territory:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                opp_adj.add((nx, ny))

    # Choose a deterministic "best" target cell to aim at
    if unclaimed:
        want_adj = self_count >= opp_count
        candidates = unclaimed
        if want_adj:
            candidates = [p for p in candidates if p in opp_adj] or unclaimed
        cx, cy = w // 2, h // 2
        # If behind, prefer closer targets; if ahead, prefer spreading/locking near center slightly
        if self_count >= opp_count:
            best = min(candidates, key=lambda p: (abs(p[0]-sx)+abs(p[1]-sy), abs(p[0]-cx)+abs(p[1]-cy), p[0], p[1]))
        else:
            best = min(candidates, key=lambda p: (-(1 if p in opp_adj else 0), abs(p[0]-ox)+abs(p[1]-oy), abs(p[0]-sx)+abs(p[1]-sy), p[0], p[1]))
        tx, ty = best
    else:
        # No unclaimed: head into opponent territory to force flips
        if opp_territory:
            # target closest opponent territory cell (deterministic)
            best = min(opp_territory, key=lambda p: (abs(p[0]-sx)+abs(p[1]-sy), p[0], p[1]))
            tx, ty = best
        else:
            # Otherwise drift toward center
            tx, ty = (w // 2, h // 2)

    # Evaluate one-step moves
    best_move = [0, 0]
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        pos = (nx, ny)
        # Base: reduce distance to target
        d_t = abs(nx - tx) + abs(ny - ty)
        score = -2 * d_t
        # If we can flip/claim now, boost
        if pos in opp_territory:
            score += 120
        elif pos in self_territory:
            score += 10
        else:
            # unclaimed or edge: claim value
            score += 35 if pos in opp_adj else 22
        # Slightly discourage moving directly into opponent's cell
        score -= 6 * (1 if (nx == ox and ny == oy) else 0)
        # Prefer not to oscillate too hard: tie-break by distance to opponent (counterclaim pressure)
        score += 2 * (abs(nx - ox) + abs(ny - oy)) * (-1 if self_count < opp_count else 1) * 0.01

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move