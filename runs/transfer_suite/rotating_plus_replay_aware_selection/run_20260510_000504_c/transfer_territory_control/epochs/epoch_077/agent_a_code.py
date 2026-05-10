def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    if resources:
        tx, ty = resources[0]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]

    opp_pos = tuple(observation.get("opponent_position") or [w - 1, h - 1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    def cell_score(x, y):
        if (x, y) in obstacles:
            return -10**18
        score = 0
        if (x, y) in opp_terr:
            score += 40  # likely flip on entry
        if (x, y) in self_terr:
            score += 8
        if (x, y) in unclaimed:
            score += 18

        # Frontier pressure: prefer squares that expand our boundary
        if self_terr:
            for nx, ny in neigh8(x, y):
                if (nx, ny) in opp_terr:
                    score += 6
                if (nx, ny) in unclaimed:
                    score += 4

        # Head toward opponent territory / position when relevant
        if opp_terr:
            # Use nearest-terr distance approximation via a small deterministic scan
            mind = 10**9
            found = False
            for ox, oy in opp_terr:
                # cheap early pruning: only consider those not too far diagonally
                d = abs(ox - x) + abs(oy - y)
                if d < mind:
                    mind = d
                    found = True
                if mind == 0:
                    break
            if found:
                score += max(0, 20 - mind)

        # Mild attraction to opponent position to intercept sweepers
        oxp, oyp = opp_pos
        score += max(0, 10 - (abs(oxp - x) + abs(oyp - y)))
        return score

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic: engine would keep us, so score as stay
        sc = cell_score(nx, ny)
        if sc > best_score or (sc == best_score and (dx, dy) < best):
            best_score = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]