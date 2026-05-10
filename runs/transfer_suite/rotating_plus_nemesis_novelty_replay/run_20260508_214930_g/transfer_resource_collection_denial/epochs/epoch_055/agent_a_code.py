def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                self_d = max(abs(x - sx), abs(y - sy))
                opp_d = max(abs(x - ox), abs(y - oy))
                candidates.append((x, y, self_d, opp_d))

    if not candidates:
        return [0, 0]

    # Two-mode deterministic policy to avoid repeating a single niche.
    # Mode A: race resources where we are ahead.
    # Mode B: nearest-resource to secure early pickups.
    turn = int(observation.get("turn_index", 0))
    if turn % 2 == 0:
        tx, ty = min(candidates, key=lambda t: (-(t[3] - t[2]), t[2], t[0], t[1]))[0:2]
    else:
        tx, ty = min(candidates, key=lambda t: (t[2], t[0], t[1]))[0:2]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        dist = max(abs(tx - nx), abs(ty - ny))
        cur = max(abs(tx - sx), abs(ty - sy))
        # Prefer progress; slight preference to moving vs standing for determinism/escaping stalls.
        key = (dist, -((dx != 0) or (dy != 0)), abs(dx) + abs(dy), dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]