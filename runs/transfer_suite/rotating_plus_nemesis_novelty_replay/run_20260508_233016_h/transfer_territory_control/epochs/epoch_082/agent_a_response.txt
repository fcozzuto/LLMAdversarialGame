def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        d_me = abs(x - sx) + abs(y - sy)
        d_opp = abs(x - ox) + abs(y - oy)
        base = -d_me
        if (x, y) in oppT:
            base += 500  # flipping
        elif (x, y) in selfT:
            base += 40   # consolidate
        else:
            base += 120  # unclaimed
        # Prefer edge/contested
        edge = (x == 0 or x == w - 1 or y == 0 or y == h - 1)
        base += 30 if edge else 0
        # Prefer moving closer to opponent-controlled frontier (approx)
        if unclaimed:
            base += max(0, 40 - (min(abs(x - ax) + abs(y - ay) for ax, ay in oppT) if oppT else 999))
        # Slightly avoid dead zones near obstacles count
        adj_obs = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                adj_obs += 1
        base -= adj_obs * 6
        # Bias toward middle early/mid game to avoid being pinched
        t = observation["turn_index"]
        bias_to_center = 16 - (abs(x - w // 2) + abs(y - h // 2))
        base += bias_to_center * (0.5 if t < 40 else 0.2)
        return base

    # Pick best immediate move by scoring reachable destination cells.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = score_cell(nx, ny)
        # If staying on own territory, allow only if we can't reach good unclaimed/opp cells
        if (nx, ny) in selfT and (nx, ny) not in oppT and val < 30:
            val -= 25
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    # If all moves look bad (e.g., surrounded), deterministically step toward freer direction
    if best_val < -1000:
        for dx, dy in sorted(candidates):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]