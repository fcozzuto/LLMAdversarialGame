def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    unclaimed = observation.get("unclaimed_cells") or []
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_target():
        if unclaimed:
            def key(c):
                x, y = c
                near_us = man(x, y, sx, sy)
                near_opp = man(x, y, ox, oy)
                edge_bonus = 3 if (x in (0, w - 1) or y in (0, h - 1)) else 0
                hit_opp = 8 if (x, y) in oppT else 0
                return near_us * 2 + near_opp - edge_bonus - hit_opp
            return sorted([tuple(c) for c in unclaimed], key=key)[:10]
        return []

    targets = best_target()
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If no unclaimed, keep expanding toward middle while preferring staying away from obstacles
    if not targets:
        tx, ty = w // 2, h // 2
        def score_move(dx, dy):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles or not inb(nx, ny):
                return -10**9
            return -man(nx, ny, tx, ty) - (5 if (nx, ny) in oppT else 0) + (2 if (nx, ny) in selfT else 0)
        best = max(candidates, key=lambda d: score_move(d[0], d[1]))
        return [int(best[0]), int(best[1])]

    # Evaluate next step by progress toward a small set of targets; also prefer moves that enter opponent territory
    def score_next(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        base = 0
        if (nx, ny) in oppT:
            base += 120
        if (nx, ny) in selfT:
            base += 10
        # choose closest target after move deterministically
        best_t = min(targets, key=lambda t: man(nx, ny, t[0], t[1]))
        dist = man(nx, ny, best_t[0], best_t[1])
        # also reward moving toward/against opponent depending on proximity
        dist_opp = man(nx, ny, ox, oy)
        return base - dist * 3 - dist_opp // 2

    best_dx, best_dy = max(candidates, key=lambda d: score_next(d[0], d[1]))
    return [int(best_dx), int(best_dy)]