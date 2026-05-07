def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        ax, ay, bx, by = a - c, b - d, a - c, b - d
        x = abs(a - c)
        y = abs(b - d)
        return x if x > y else y

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda d: (d[0], d[1]))  # deterministic tie-break

    best_score = None
    best_move = (0, 0)

    # Prefer moves that reduce our distance to the best resource while accounting for opponent arrival.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep us in place
        score = 0.0
        best_res = None
        best_val = None

        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Lower is better: prioritize closer resources for us; if opponent also close, penalize.
            # Add slight "cornering": prefer resources in our movement direction (toward opponent corner).
            toward = (dx * (rx - sx) + dy * (ry - sy))
            blockish = 0.0
            if (rx, ry) in obstacles:
                continue
            val = (ds - 0.85 * do) - 0.03 * toward
            # Small preference to reduce our absolute distance overall to move toward collection.
            val += 0.01 * ds
            if best_val is None or val < best_val:
                best_val = val
                best_res = (rx, ry)

        # If we can immediately step onto a resource, take it.
        if best_res is not None and cheb(nx, ny, best_res[0], best_res[1]) == 0:
            cand = -1000.0
        else:
            rx, ry = best_res
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Also encourage distancing from opponent when ds is already small.
            cand = (ds - 0.85 * do) + 0.02 * (cheb(nx, ny, ox, oy) if ds <= 2 else 0)

        # Extra anti-stall: if opponent is closer to the currently best resource, prefer moves that improve ds most.
        if do <= ds:
            ds0 = min(cheb(sx + d[0] if inb(sx + d[0], sy + d[1]) else sx, sy + d[1] if inb(sx + d[0], sy + d[1]) else sy, r[0], r[1]) for d in dirs for r in resources[:1])
            cand -= 0.0 + 0.01 * ds0

        if best_score is None or cand < best_score:
            best_score = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]