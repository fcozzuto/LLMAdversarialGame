def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    self_set = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                self_set.add((x, y))

    opp_set = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                opp_set.add((x, y))

    unclaimed = []
    for key in ("unclaimed_cells", "unclaimed"):
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if isinstance(x, int) and isinstance(y, int) and inside(x, y) and (x, y) not in obstacles:
                    unclaimed.append((x, y))
    if not unclaimed:
        unclaimed = [p for p in self_set]  # fallback

    # Deterministic frontier sampling: closest unclaimed to current position
    unclaimed_sorted = sorted(unclaimed, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    sample = unclaimed_sorted[: min(20, len(unclaimed_sorted))]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bx, by = sx, sy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in self_set:
            base += 1
        elif (nx, ny) in opp_set:
            base += 4
        else:
            # likely unclaimed
            base += 3 if (nx, ny) in set(unclaimed_sorted) else 2

        # Prefer decreasing distance to the nearest promising unclaimed
        mind = 10**9
        for tx, ty in sample:
            d = abs(tx - nx) + abs(ty - ny)
            if d < mind:
                mind = d
        base -= mind * 0.25

        # Slightly avoid edges early unless it helps capture
        if observation.get("turn_index", 0) < 30:
            if nx in (0, w - 1) or ny in (0, h - 1):
                base -= 0.6 if (nx, ny) not in opp_set else 0.0

        if best is None or base > best or (base == best and (nx, ny) < (bx, by)):
            best = base
            bx, by = nx, ny

    return [bx - sx, by - sy]