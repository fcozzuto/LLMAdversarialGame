def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        for p in v or []:
            try:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
            except Exception:
                pass
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    opp_terr = to_set(observation.get("opponent_territory"))
    self_terr = to_set(observation.get("self_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer central expansion while contesting territory.
        dist_center = abs(nx - cx) + abs(ny - cy)
        center_score = 160 - 12 * dist_center

        score = 0
        if (nx, ny) in unclaimed:
            score += 120
        if (nx, ny) in self_terr:
            score += 30
        if (nx, ny) in opp_terr:
            score += 55  # flipping on entry: contest opponent-held cells

        # Subtle control: reduce oscillations by favoring moves that don't increase distance to target cell
        # Here target is the nearest central unclaimed/opponent territory to the center.
        if observation.get("unclaimed_cells"):
            # Deterministic nearest-to-center target among a small subset (no big search).
            targets = observation["unclaimed_cells"]
        else:
            targets = observation.get("opponent_territory") or []
        tx, ty = None, None
        if targets:
            # take first few candidates deterministically
            cand = targets[:min(12, len(targets))]
            best_t = None
            best_td = 10**9
            for p in cand:
                try:
                    x, y = int(p[0]), int(p[1])
                except Exception:
                    continue
                d = abs(x - cx) + abs(y - cy)
                if d < best_td or (d == best_td and (x < best_t[0] if best_t else True)):
                    best_td = d
                    best_t = (x, y)
            if best_t:
                tx, ty = best_t
        if tx is not None:
            before = abs(sx - tx) + abs(sy - ty)
            after = abs(nx - tx) + abs(ny - ty)
            score += 10 * (before - after)

        # Slightly discourage moving away from opponent late (more flipping opportunities)
        score += 2 * (abs(nx - ox) + abs(ny - oy) - (abs(sx - ox) + abs(sy - oy)))

        score += center_score

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move