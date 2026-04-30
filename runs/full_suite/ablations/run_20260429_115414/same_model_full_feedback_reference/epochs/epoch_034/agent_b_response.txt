def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def md(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def sort_key(r):
        x, y = r
        return (x * 31 + y, y, x)

    resources.sort(key=sort_key)

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my = (nx, ny)

        if resources:
            best = None
            for rx, ry in resources:
                r = (rx, ry)
                ds = md(my, r)
                do = md((ox, oy), r)
                # Prefer states where we can arrive no later than opponent (and sooner).
                val = (do - ds) * 2 - ds
                if best is None or val > best[0]:
                    best = (val, ds, r)
            base = best[0]
            # Anticipate immediate contest: if opponent is also adjacent to the target, reduce.
            contested = 0
            for rx, ry in resources[:4]:
                if md((ox, oy), (rx, ry)) <= 1 and md(my, (rx, ry)) <= 1:
                    contested += 1
            score = base - contested * 1.5
        else:
            # No visible resources: head toward center.
            cx, cy = (W - 1) // 2, (H - 1) // 2
            score = -md(my, (cx, cy)) + (md((ox, oy), (cx, cy)) * 0.2)

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]