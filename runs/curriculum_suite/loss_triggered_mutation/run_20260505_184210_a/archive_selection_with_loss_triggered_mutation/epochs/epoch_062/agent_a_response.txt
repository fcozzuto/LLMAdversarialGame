def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource that maximizes advantage: (opp_dist - self_dist).
    best = None
    best_key = None
    for (rx, ry) in resources:
        sd = md((sx, sy), (rx, ry))
        od = md((ox, oy), (rx, ry))
        # Prefer resources where we are closer; break ties by smaller self distance, then by lexicographic cell.
        key = (od - sd, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Greedy one-step toward target, but avoid obstacles; deterministically break ties by best next-cell advantage.
    cx, cy = sx, sy
    chosen = (0, 0)
    chosen_key = None
    for dx, dy in moves:
        nx, ny = cx + dx, cy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = md((nx, ny), (tx, ty))
        # Secondary objective: if target is contested, also prefer moves that keep us ahead over opponent for any resource.
        # Use a cheap approximation with the same target cell only to stay concise/deterministic.
        nosd = nsd  # same reference for stability
        key = (-nosd, abs(nx - tx) + abs(ny - ty), dx, dy)
        if chosen_key is None or key < chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    # If all moves blocked, stay.
    return [int(chosen[0]), int(chosen[1])]