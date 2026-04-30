def choose_move(observation):
    gw = observation["grid_width"]
    gh = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                cand.append((dx, dy))
    if not cand:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = ox, oy
        best = None
        bestv = 10**9
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            v = dist((nx, ny), (tx, ty))
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    dirs = [(p[0], p[1]) for p in resources]
    best = None
    bestv = 10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        base = 0
        farthest = 0
        for tx, ty in dirs:
            d = dist((nx, ny), (tx, ty))
            od = dist((ox, oy), (tx, ty))
            farthest = max(farthest, d)
            # Prefer resources we can reach no later than opponent; penalize contested ones.
            penalty = 0
            if od < d:
                penalty = (d - od) * 12 + 30
            base += d + penalty
        # Encourage moving toward some resource (not just minimizing sum) and avoid stalling.
        v = base + farthest * 0.5 + (abs(dx) + abs(dy) == 0) * 5
        if v < bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]