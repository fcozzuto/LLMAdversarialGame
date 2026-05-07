def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    # Evaluate each move by resulting "competitive pressure" over a small set of best targets.
    # Deterministic: sort resources by static key and consider top K.
    resources_sorted = sorted(resources, key=lambda t: (-dist((ox, oy), t) + dist((sx, sy), t), dist((sx, sy), t), (t[1] * w + t[0])))
    K = 5 if len(resources_sorted) >= 5 else len(resources_sorted)
    targets = resources_sorted[:K]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer moves that put us closer to a target where opponent is not closer.
        cur = 0
        for tx, ty in targets:
            sd = dist((nx, ny), (tx, ty))
            od = dist((ox, oy), (tx, ty))
            adv = od - sd
            if sd == 0:
                cur += 200000  # immediate collection
            cur += adv * 10000 - sd * 50 + (-(tx + ty) % 9)
        # Small bias to avoid drifting aimlessly
        cur += -(abs(nx - ox) + abs(ny - oy)) * 1

        # Deterministic tie-break
        tie = (-(dx == 0 and dy == 0), (dx + 2) + (dy + 2) * 3)

        if best is None or (cur, tie) > best[0]:
            best = ((cur, tie), [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]