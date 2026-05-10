def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(c) for c in (observation.get("unclaimed_cells") or [])]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a deterministic target: near the front (closest to opponent), prefer edge unclaimed, avoid far-from-us too much.
    if unclaimed:
        def edge_bias(x, y):
            return (x in (0, w - 1)) + (y in (0, h - 1))
        # Deterministic tie-breaker: lexicographic
        best_target = None
        best_key = None
        for x, y in unclaimed:
            if not inb(x, y) or (x, y) in obstacles:
                continue
            key = (
                -edge_bias(x, y) * 50,                 # favor edges first
                man(x, y, ox, oy),                   # then near opponent
                man(x, y, sx, sy),                   # and reachable
                (x, y)
            )
            if best_key is None or key < best_key:
                best_key = key
                best_target = (x, y)
    else:
        # If nothing unclaimed, "shepherd" toward center and away from opponent slightly.
        best_target = (w // 2, h // 2)

    tx, ty = best_target

    # Evaluate each move by immediate territory gain potential and progress toward target; discourage obstacle hits.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**12
        else:
            cell = (nx, ny)
            val = 0
            if cell in oppT:
                val += 2200  # flipping opponent territory is very valuable
            if cell in selfT:
                val += 30
            # Unclaimed is generally good to expand into; edges are slightly better.
            if cell not in selfT and cell not in oppT:
                val += 900
                if nx in (0, w - 1) or ny in (0, h - 1):
                    val += 120
            # Progress toward chosen target and keep some distance from opponent (avoid getting swept).
            dist_cur = man(sx, sy, tx, ty)
            dist_nxt = man(nx, ny, tx, ty)
            val += (dist_cur - dist_nxt) * 25
            val += (man(nx, ny, ox, oy) - man(sx, sy, ox, oy)) * 8
            # Mild preference to avoid getting stuck near opponent if unclaimed empty.
            if not unclaimed:
                val += (man(nx, ny, ox, oy) - man(sx, sy, ox, oy)) * 3
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]