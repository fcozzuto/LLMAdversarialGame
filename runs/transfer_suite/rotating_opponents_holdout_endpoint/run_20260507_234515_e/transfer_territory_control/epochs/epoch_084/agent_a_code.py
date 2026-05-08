def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))

    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or [])]
    if unclaimed:
        targets = unclaimed
        mode = 0  # expand to unclaimed
    elif opp_terr:
        targets = list(opp_terr)
        mode = 1  # contest
    else:
        targets = [(ox, oy)]
        mode = 2

    def dman(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # pick a primary target deterministically: min (distance, then lexicographic)
    primary = min(targets, key=lambda t: (dman((sx, sy), t), t[0], t[1]))

    best = None
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx, dy) != (0, 0):
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if (nx, ny) in obstacles:
                    continue

            # evaluate move using target attraction + cell-type bonus
            dist = dman((nx, ny), primary)
            val = -dist

            if (nx, ny) in unclaimed:
                val += 80 if mode == 0 else 30
            if (nx, ny) in opp_terr:
                val += 60 if mode != 0 else 50
            if (nx, ny) in self_terr:
                val -= 5  # slight avoid backtracking unless needed

            # also prefer getting closer to opponent if we have no unclaimed
            if mode != 0:
                val += -0.3 * dman((nx, ny), (ox, oy))

            # deterministic tie-break: prefer smallest (dx,dy) in scan order already; add lex value
            val += -0.001 * (abs(dx) + abs(dy))

            if val > best_val:
                best_val = val
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best