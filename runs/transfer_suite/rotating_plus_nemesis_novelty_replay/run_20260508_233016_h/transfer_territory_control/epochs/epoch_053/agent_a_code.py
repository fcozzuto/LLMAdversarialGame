def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose goals: prioritize near opponent territory; otherwise near any unclaimed.
    opp_front_targets = []
    for ax, ay in opp_t:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = ax + dx, ay + dy
            if inb(nx, ny) and ((nx, ny) in unclaimed):
                opp_front_targets.append((nx, ny))
    if not opp_front_targets:
        opp_front_targets = list(unclaimed)
    if not opp_front_targets:
        opp_front_targets = [(w // 2, h // 2)]

    # Deterministic tie-breaking: prefer moves with smaller (abs(dx)+abs(dy)), then lexicographic dx,dy
    best = None
    best_val = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in opp_t:
            val += 600  # immediate counter-claim
        if (nx, ny) in unclaimed:
            val += 120  # expansion into free area
        if (nx, ny) in self_t:
            val += 20   # keep momentum

        # Reduce distance to targets, but don't blunder too close to opponent.
        d_t = min(man(nx, ny, tx, ty) for tx, ty in opp_front_targets[:40])
        val += 60 - 15 * d_t

        d_o = man(nx, ny, ox, oy)
        val += 10 * d_o if d_o >= 2 else 0  # avoid immediate contact unless capturing

        # Bias toward progressing away from own start corner and toward opponent side using positions.
        # (Static heuristic, deterministic)
        val += (nx - sx) * 2 + (ny - sy) * 2

        tie = (abs(dx) + abs(dy), dx, dy)
        if val > best_val or (val == best_val and (best is None or tie < best[0])):
            best_val = val
            best = (tie, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]