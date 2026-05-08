def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that (1) steal adjacent opponent cells when safe, (2) expand into unclaimed, (3) avoid risky proximity.
    best = None
    best_score = -10**18

    def neigh8(x, y):
        s = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if (nx, ny) in self_terr:
                        s += 2
                    if (nx, ny) in opp_terr:
                        s -= 2
                    if (nx, ny) in unclaimed:
                        s += 1
        return s

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            # allow engine to reject; treat as invalid by skipping
            continue

        score = 0
        in_opp = (nx, ny) in opp_terr
        in_un = (nx, ny) in unclaimed
        in_self = (nx, ny) in self_terr

        d_op = dist((nx, ny), (ox, oy))
        score += -6 if d_op <= 1 else 0
        score += (3 if d_op >= 6 else 0)

        score += neigh8(nx, ny)

        # Territory mechanics: entering opponent flips control, so stealing is valuable if not immediately surrounded by opp.
        if in_opp:
            score += 10
            # If opponent is very close, their counterclaim likely negates; reduce.
            score += -4 if dist((nx, ny), (ox, oy)) <= 2 else 0
        elif in_un:
            score += 7
        elif in_self:
            score += 1
        else:
            score += 0

        # Strongly prefer progressing toward the nearest unclaimed boundary when not under immediate pressure.
        if unclaimed:
            # approximate "frontier": target distance in manhattan, but only reward slightly
            score += max(0, 4 - min(dist((nx, ny), t) for t in unclaimed) // 2)

        # Deterministic tie-break: prefer staying still last.
        score += -0.01 if (dx == 0 and dy == 0) else 0.0

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]