def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []) if x is not None)
    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = list(unclaimed) if unclaimed else list(opp_t)
    if not targets:
        tx, ty = ox, oy
    else:
        # nearest target with deterministic tie-break
        tx, ty = min(targets, key=lambda c: (man((sx, sy), c), c[0], c[1]))

    best = None
    best_score = None

    # Pressure direction towards opponent (deterministic)
    px = 1 if ox > sx else (-1 if ox < sx else 0)
    py = 1 if oy > sy else (-1 if oy < sy else 0)

    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            cand_score = -10**9
        else:
            cell = (nx, ny)
            # Immediate territory value
            if cell in opp_t:
                base = 120
            elif cell in unclaimed:
                base = 70
            elif cell in self_t:
                base = 10
            else:
                base = 25

            # Avoid stepping away from the chosen target
            d_before = man((sx, sy), (tx, ty))
            d_after = man((nx, ny), (tx, ty))
            progress = 20 * (d_before - d_after)

            # Tactical: if moving into opponent territory, prefer also to move away from our own corner
            away_from_corner = abs(nx - 0) + abs(ny - 0)
            pressure = 8 * (dx * px + dy * py)

            # Defensive: discourage moving adjacent to obstacles when not gaining much
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    xx, yy = nx + ax, ny + ay
                    if (xx, yy) in obstacles:
                        adj_obs += 1

            cand_score = base + progress + pressure + (2 * away_from_corner) - (6 * adj_obs)

        if best_score is None or cand_score > best_score:
            best_score = cand_score
            best = [dx, dy]

    # Guaranteed deterministic return
    return [int(best[0]), int(best[1])]