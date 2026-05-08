def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick best next step: maximize (prefer moving closer to nearest unclaimed), avoid obstacles.
    best = None
    best_val = None

    if unclaimed:
        targets = list(unclaimed)
    else:
        # fallback: head toward opponent territory frontier-ish using unclaimed as whole map not possible
        targets = [(x, y) for x in range(w) for y in range(h) if (x, y) not in obstacles]

    # Precompute nearest target distance from current position
    # (limit by taking few closest targets to keep deterministic and short)
    def dist(x, y):
        return abs(sx - x) + abs(sy - y)

    targets.sort(key=lambda t: dist(t[0], t[1]))
    targets = targets[:20] if targets else [(ox, oy)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer decreasing distance to nearest unclaimed; if none, approach opponent.
        if unclaimed:
            d = 10**9
            for tx, ty in targets:
                d2 = abs(nx - tx) + abs(ny - ty)
                if d2 < d:
                    d = d2
            # Slight tie-break toward moving away from opponent if close (defensive), otherwise toward targets.
            adv = -abs(nx - ox) - abs(ny - oy)
            val = (-d, adv)
        else:
            d = abs(nx - ox) + abs(ny - oy)
            val = (-d, 0)
        if best is None or val > best_val:
            best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]