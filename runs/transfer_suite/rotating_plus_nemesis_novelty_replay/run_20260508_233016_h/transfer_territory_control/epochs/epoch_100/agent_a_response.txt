def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(c) for c in (observation.get("unclaimed_cells") or [])]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not unclaimed:
        unclaimed = []

    # Prefer targets that are likely to swing territory: adjacent opponent cells or high-value unclaimed
    # Deterministic: take top K by key.
    K = 18
    if unclaimed:
        def tgt_key(c):
            x, y = c
            dist_self = man(x, y, sx, sy)
            dist_opp = man(x, y, ox, oy)
            near_opp = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if (nx, ny) in oppT:
                    near_opp = 4
                    break
            # Penalty for self territory (already controlled); reward for potential contest (near opponent)
            already = 6 if (x, y) in selfT else 0
            return (dist_self - 0.6 * dist_opp) + already - near_opp
        targets = sorted(unclaimed, key=tgt_key)[:K]
    else:
        # If no unclaimed, chase opponent boundary cells (cells adjacent to opponent territory)
        targets = []
        for (x, y) in oppT:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in oppT and (nx, ny) not in obstacles:
                    targets.append((nx, ny))
        targets = list(dict.fromkeys(targets))[:K]

    if not targets:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Immediate value heuristic: entering opponent territory is strongly rewarded due to flipping.
        immediate = 0
        if (nx, ny) in oppT:
            immediate += 120
        elif (nx, ny) in selfT:
            immediate += 10
        else:
            immediate += 22 if (nx, ny) in unclaimed else 0

        # Distance-to-best-target tradeoff
        # Evaluate a few closest targets only (cheap, deterministic)
        local_best = 10**9
        for tx, ty in targets[:10]:
            d = man(nx, ny, tx, ty)
            if d < local_best:
                local_best = d

        # Avoid stepping "away" from boundary when contesting: slight preference for decreasing distance to opponent
        boundary = man(nx, ny, ox, oy) - man(sx, sy, ox, oy)
        score = immediate - local_best * 3 - boundary * 2

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]