def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed_list = observation.get("unclaimed_cells") or []
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(c) for c in unclaimed_list]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    blocked = set()

    # If we can, target frontier: unclaimed near us OR boundary-adjacent to opponent.
    # Pick a small deterministic subset.
    target_pool = []
    if unclaimed:
        for c in unclaimed:
            x, y = c
            if (x, y) in oppT:
                continue
            d_us = man(x, y, sx, sy)
            d_opp = man(x, y, ox, oy)
            # Prefer closer to us, but also nearer the opponent's influence.
            # Slight edge bias to fight territory edges.
            edge_bias = (x == 0) + (x == w - 1) + (y == 0) + (y == h - 1)
            score = d_us * 2 - d_opp - edge_bias * 3
            # Also prefer expanding where we already have territory (frontline feel).
            if (x, y) in selfT:
                score -= 10
            target_pool.append((score, x, y))
        target_pool.sort(key=lambda t: (t[0], t[1], t[2]))
        target_pool = target_pool[:18]
    else:
        # No unclaimed cells: push toward opponent territory boundary (to flip on entry).
        target_pool = [(0, ox, oy)]

    # Helper: best target move utility with local evaluation.
    # Favor entering opponent territory (flipping), otherwise entering unclaimed.
    unclaimed_set = set(unclaimed)

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break: prefer lexicographically smaller (dx,dy) among equals.
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        base = 0
        if cell in oppT:
            base += 1200  # strong: direct flipping
        elif cell in unclaimed_set:
            base += 300  # claiming unclaimed
        elif cell in selfT:
            base += 30  # maintain control and continue route
        else:
            base -= 5  # stray into area we can't claim (likely already opponent but not in sets)

        # Distance to best few targets
        dist_best = 10**9
        for _, tx, ty in target_pool[:10]:
            d = man(nx, ny, tx, ty)
            if d < dist_best:
                dist_best = d
        # Also bias away from getting stuck on our own territory far from frontier
        toward_opp = man(nx, ny, ox, oy)

        val = base - dist_best * 6 - toward_opp * 0.4
        # Prefer continuing direction if already near a good frontier
        if cell in selfT:
            # keep moving: add small penalty for staying still
            val -= (dx == 0 and dy == 0) * 18
        # Deterministic tie-break
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    # If all moves blocked, stay
    if best_val == -10**18:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]