def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mdist(a, b):
        ax, ay = a
        bx, by = b
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    targets = list(unclaimed) if unclaimed else (list(resources) if resources else [])
    if not targets:
        # Fall back: press toward opponent territory or center
        targets = list(opp_terr) if opp_terr else [(w // 2, h // 2)]

    # Deterministic nearest target (tie by lexicographic)
    best_t = None
    best_d = 10**9
    for t in targets:
        d = mdist((sx, sy), t)
        if d < best_d or (d == best_d and (t[0], t[1]) < (best_t[0], best_t[1])):
            best_d = d
            best_t = t

    tx, ty = best_t

    # Evaluate candidate next cells deterministically
    ordered = dirs[:]  # fixed
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        d = mdist(cell, (tx, ty))
        score = -d * 10

        if cell in unclaimed:
            score += 40
        if cell in opp_terr:
            score += 25  # flipping on entry
            # prefer breaking through toward target
            score += max(0, best_d - d) * 3
        if cell in self_terr:
            score += 6
        # Avoid staying if it doesn't improve
        if dx == 0 and dy == 0:
            score -= 3

        # Prefer moves that also reduce distance from opponent if we're close
        if opp_terr:
            od = 10**9
            for ot in list(opp_terr)[:12]:
                t2 = mdist(cell, ot)
                if t2 < od:
                    od = t2
            score += max(0, 4 - od) * 2

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]