def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda p: (dist2(sx, sy, p[0], p[1]) - dist2(ox, oy, p[0], p[1]), p[0], p[1]))
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            key = (dist2(nx, ny, tx, ty), dist2(nx, ny, ox, oy), nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    # Evaluate each move by the best "lead" on any resource; prefer moves that create self lead.
    best_key, best_move = None, [0, 0]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: continue

        # Target scoring from this next position
        local_best = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Lead: smaller means opponent is closer; bigger means we're closer. Use large weight.
            lead = do - ds
            # Prefer immediate collection and then lead; tie-break by distance to reduce future drift.
            key = (-(1000 if lead > 0 else (0 if lead == 0 else 0)) + (-lead), ds, dist2(nx, ny, rx, ry), rx, ry)
            if local_best is None or key < local_best[0]:
                local_best = (key, ds, do, rx, ry)

        # If a move goes directly onto a resource, that's usually optimal; add strong deterministic bonus.
        onto = any((nx == rx and ny == ry) for rx, ry in resources)
        key2 = (0 if onto else 1, local_best[0] if local_best else (0, 0, 0, 0, 0), nx, ny, dx, dy)

        if best_key is None or key2 < best_key:
            best_key, best_move = key2, [dx, dy]

    return best_move if best_move else [0, 0]